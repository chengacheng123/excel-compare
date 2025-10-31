import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import xlsxwriter

# ========================
# 页面配置
# ========================
st.set_page_config(
    page_title="📊 Excel精确对比工具",
    page_icon="📊",
    layout="wide"
)

# ========================
# 页面标题
# ========================
st.title("📊 Excel精确键值对比工具")
st.markdown("上传两个Excel文件，选择匹配字段，基于键值进行精确对比")

# ========================
# 上传文件
# ========================
file1 = st.file_uploader("📤 上传【第一个】Excel文件", type=["xlsx", "xls"], key="file1")
file2 = st.file_uploader("📥 上传【第二个】Excel文件", type=["xlsx", "xls"], key="file2")

if file1 and file2:
    try:
        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)

        st.success("✅ 文件读取成功！")

        col1, col2 = st.columns(2)
        with col1:
            st.write("第一个文件预览：")
            st.dataframe(df1.head(3), use_container_width=True)
            st.write(f"数据行数: {len(df1)}")
        with col2:
            st.write("第二个文件预览：")
            st.dataframe(df2.head(3), use_container_width=True)
            st.write(f"数据行数: {len(df2)}")

        # 获取列名
        columns = df1.columns.tolist()
        if len(columns) < 1:
            st.error("❌ 表格没有列，请检查文件")
        else:
            # 选择匹配字段（多选）
            key_columns = st.multiselect(
                "请选择用于数据匹配的字段（可多选）",
                options=columns,
                default=columns[0] if columns else None
            )

            if len(key_columns) == 0:
                st.warning("⚠️ 请至少选择一个匹配字段")
            else:
                if st.button("🔍 开始精确对比"):
                    with st.spinner("正在生成精确对比报告..."):
                        # 创建唯一键
                        df1['__key__'] = df1[key_columns].astype(str).apply(lambda x: '｜'.join(x), axis=1)
                        df2['__key__'] = df2[key_columns].astype(str).apply(lambda x: '｜'.join(x), axis=1)

                        # 合并对比
                        combined = pd.merge(
                            df1,
                            df2,
                            on='__key__',
                            how='outer',
                            suffixes=('_文件1', '_文件2'),
                            indicator=True
                        )

                        # 找出差异数据
                        only_in_file1 = combined[combined['_merge'] == 'left_only'].copy()
                        only_in_file2 = combined[combined['_merge'] == 'right_only'].copy()
                        common = combined[combined['_merge'] == 'both'].copy()

                        # ========================
                        # 生成精确对比的Excel报告
                        # ========================
                        output = BytesIO()

                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            workbook = writer.book

                            # 定义颜色格式
                            format_green = workbook.add_format(
                                {'bg_color': '#C6EFCE', 'font_color': '#006100'})  # 浅绿 - 仅文件1有
                            format_red = workbook.add_format(
                                {'bg_color': '#FFC7CE', 'font_color': '#9C0006'})  # 浅红 - 仅文件2有
                            format_yellow = workbook.add_format(
                                {'bg_color': '#FFEB9C', 'font_color': '#9C6500'})  # 浅黄 - 字段差异
                            format_header = workbook.add_format(
                                {'bold': True, 'bg_color': '#366092', 'font_color': 'white'})

                            # 创建精确对比数据框
                            comparison_data = []

                            # 获取所有列名（按原始顺序）
                            all_columns = df1.columns.tolist()  # 使用第一个文件的列顺序

                            # 所有唯一的键值
                            all_keys = set(df1['__key__'].tolist() + df2['__key__'].tolist())

                            for key in all_keys:
                                file1_row = df1[df1['__key__'] == key]
                                file2_row = df2[df2['__key__'] == key]

                                row_data = {}
                                row_data['匹配字段'] = key

                                # 第一个文件数据（按原始列顺序）
                                if not file1_row.empty:
                                    for col in all_columns:
                                        row_data[f'文件1_{col}'] = file1_row.iloc[0][col]
                                else:
                                    for col in all_columns:
                                        row_data[f'文件1_{col}'] = ""

                                # 第二个文件数据（按原始列顺序）
                                if not file2_row.empty:
                                    for col in all_columns:
                                        row_data[f'文件2_{col}'] = file2_row.iloc[0][col]
                                else:
                                    for col in all_columns:
                                        row_data[f'文件2_{col}'] = ""

                                # 确定状态
                                if not file1_row.empty and not file2_row.empty:
                                    # 检查字段差异
                                    has_difference = False
                                    for col in all_columns:
                                        if col not in key_columns:  # 跳过键列
                                            val1 = file1_row.iloc[0][col] if not pd.isna(file1_row.iloc[0][col]) else ""
                                            val2 = file2_row.iloc[0][col] if not pd.isna(file2_row.iloc[0][col]) else ""
                                            if str(val1) != str(val2):
                                                has_difference = True
                                                break

                                    if has_difference:
                                        row_data['对比状态'] = '字段差异'
                                    else:
                                        row_data['对比状态'] = '数据一致'
                                elif not file1_row.empty:
                                    row_data['对比状态'] = '仅文件1有'
                                elif not file2_row.empty:
                                    row_data['对比状态'] = '仅文件2有'

                                comparison_data.append(row_data)

                            comparison_df = pd.DataFrame(comparison_data)

                            # 重新排序列：匹配字段 + 文件1所有列 + 文件2所有列 + 对比状态
                            file1_columns = [f'文件1_{col}' for col in all_columns]
                            file2_columns = [f'文件2_{col}' for col in all_columns]
                            final_columns = ['匹配字段'] + file1_columns + file2_columns + ['对比状态']
                            comparison_df = comparison_df[final_columns]

                            # 写入Excel
                            comparison_df.to_excel(writer, sheet_name='精确键值对比', index=False)

                            # 获取工作表对象
                            worksheet = writer.sheets['精确键值对比']

                            # 设置列宽
                            for idx, col in enumerate(comparison_df.columns):
                                if col == '匹配字段':
                                    worksheet.set_column(idx, idx, 30)
                                else:
                                    worksheet.set_column(idx, idx, 20)

                            # 应用颜色标识
                            for row_num in range(1, len(comparison_df) + 1):
                                status = comparison_df.iloc[row_num - 1]['对比状态']
                                if status == '仅文件1有':
                                    worksheet.set_row(row_num, None, format_green)
                                elif status == '仅文件2有':
                                    worksheet.set_row(row_num, None, format_red)
                                elif status == '字段差异':
                                    worksheet.set_row(row_num, None, format_yellow)

                            # 设置标题行格式
                            for col_num, value in enumerate(comparison_df.columns.values):
                                worksheet.write(0, col_num, value, format_header)

                            # 添加分隔线
                            file1_cols_count = len(file1_columns)
                            separator_col = len(['匹配字段']) + file1_cols_count
                            worksheet.set_column(separator_col - 1, separator_col - 1, 20, format_header)
                            worksheet.set_column(separator_col, separator_col, 20, format_header)

                            # 差异汇总表
                            status_counts = {
                                '数据一致': len(comparison_df[comparison_df['对比状态'] == '数据一致']),
                                '仅文件1有': len(comparison_df[comparison_df['对比状态'] == '仅文件1有']),
                                '仅文件2有': len(comparison_df[comparison_df['对比状态'] == '仅文件2有']),
                                '字段差异': len(comparison_df[comparison_df['对比状态'] == '字段差异'])
                            }

                            summary_data = {
                                '对比状态': ['数据一致', '仅文件1有', '仅文件2有', '字段差异', '文件1总行数',
                                             '文件2总行数'],
                                '数量': [
                                    status_counts['数据一致'],
                                    status_counts['仅文件1有'],
                                    status_counts['仅文件2有'],
                                    status_counts['字段差异'],
                                    len(df1),
                                    len(df2)
                                ],
                                '说明': [
                                    '两个文件完全一致的数据',
                                    '仅出现在第一个文件的数据',
                                    '仅出现在第二个文件的数据',
                                    '键相同但字段值不同的数据',
                                    '第一个文件总数据量',
                                    '第二个文件总数据量'
                                ]
                            }
                            summary_df = pd.DataFrame(summary_data)
                            summary_df.to_excel(writer, sheet_name='差异汇总', index=False)

                            # 设置汇总表格式
                            worksheet_summary = writer.sheets['差异汇总']
                            for idx, col in enumerate(summary_df.columns):
                                worksheet_summary.set_column(idx, idx, 25)
                            for col_num, value in enumerate(summary_df.columns.values):
                                worksheet_summary.write(0, col_num, value, format_header)

                        # ========================
                        # 在网页上展示结果
                        # ========================
                        st.subheader("📊 精确对比结果")

                        # 颜色标识说明
                        st.info("""
                        **Excel报告包含2个工作表：**
                        - 🔍 **精确键值对比**：基于匹配字段进行精确对比，左右并排显示
                        - 📈 **差异汇总**：统计信息和差异汇总

                        **颜色标识说明：**
                        - 🟢 **浅绿色**：仅出现在第一个文件的数据
                        - 🔴 **浅红色**：仅出现在第二个文件的数据  
                        - 🟡 **浅黄色**：字段值不同的数据
                        - ⚪ **无颜色**：两个文件完全一致的数据
                        """)

                        # 统计信息
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("📄 文件1总行数", len(df1))
                        col2.metric("📄 文件2总行数", len(df2))
                        col3.metric("✅ 数据一致", status_counts['数据一致'])
                        col4.metric("⚠️ 字段差异", status_counts['字段差异'])

                        # 预览对比结果
                        if not comparison_df.empty:
                            st.write("### 👀 对比结果预览")

                            # 简化预览（只显示前几列）
                            preview_columns = ['匹配字段'] + file1_columns[:3] + file2_columns[:3] + ['对比状态']
                            preview_df = comparison_df[preview_columns].head(10)

                            # 重命名预览列名，使其更简洁
                            preview_rename = {}
                            for col in preview_columns:
                                if col.startswith('文件1_'):
                                    preview_rename[col] = col.replace('文件1_', '文件1.')
                                elif col.startswith('文件2_'):
                                    preview_rename[col] = col.replace('文件2_', '文件2.')
                                else:
                                    preview_rename[col] = col
                            preview_df = preview_df.rename(columns=preview_rename)

                            st.dataframe(preview_df, use_container_width=True)

                        # 如果完全一致
                        total_differences = status_counts['仅文件1有'] + status_counts['仅文件2有'] + status_counts[
                            '字段差异']
                        if total_differences == 0:
                            st.balloons()
                            st.success("🎉 两个文件数据完全一致！")

                        excel_data = output.getvalue()

                        # 下载按钮
                        st.download_button(
                            label="📥 下载精确对比报告",
                            data=excel_data,
                            file_name=f"精确对比报告_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

    except Exception as e:
        st.error(f"❌ 处理文件时出错：{str(e)}")
        st.code(str(e))  # 显示详细错误信息