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
st.markdown("上传两个Excel文件，系统将自动标准化为以下5列，基于键值进行精确对比")

# 固定列名标准
FIXED_COLUMNS = ['替代料', '机型', '型号', '规格型号', '用量']

# 显示固定表头说明
st.info(f"""
**系统将统一使用以下5个字段作为表头：**
> {', '.join(FIXED_COLUMNS)}

请确保你的Excel文件至少包含5列，且顺序对应。
""")

# ========================
# 上传文件
# ========================
file1 = st.file_uploader("📤 上传【第一个】Excel文件", type=["xlsx", "xls"], key="file1")
file2 = st.file_uploader("📥 上传【第二个】Excel文件", type=["xlsx", "xls"], key="file2")

if file1 and file2:
    try:
        # 读取原始数据
        df1_raw = pd.read_excel(file1)
        df2_raw = pd.read_excel(file2)

        # 检查列数是否足够
        if len(df1_raw.columns) < 5:
            st.error("❌ 第一个文件的列数少于5列，无法映射到固定表头")
            st.stop()
        if len(df2_raw.columns) < 5:
            st.error("❌ 第二个文件的列数少于5列，无法映射到固定表头")
            st.stop()

        # 取前5列并重命名为固定列名
        df1 = df1_raw.iloc[:, :5].copy()
        df2 = df2_raw.iloc[:, :5].copy()
        df1.columns = FIXED_COLUMNS
        df2.columns = FIXED_COLUMNS

        st.success("✅ 文件读取成功，并已应用固定表头！")

        # 展示预览
        col1, col2 = st.columns(2)
        with col1:
            st.write("第一个文件预览（已标准化）：")
            st.dataframe(df1.head(3), use_container_width=True)
            st.write(f"数据行数: {len(df1)}")
        with col2:
            st.write("第二个文件预览（已标准化）：")
            st.dataframe(df2.head(3), use_container_width=True)
            st.write(f"数据行数: {len(df2)}")

        # 用户选择匹配字段
        key_columns = st.multiselect(
            "请选择用于数据匹配的字段（可多选）",
            options=FIXED_COLUMNS,
            default=['替代料']  # 默认选“替代料”
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

                    # 分离不同情况
                    only_in_file1 = combined[combined['_merge'] == 'left_only'].copy()
                    only_in_file2 = combined[combined['_merge'] == 'right_only'].copy()
                    common = combined[combined['_merge'] == 'both'].copy()

                    # ========================
                    # 生成精确对比的Excel报告
                    # ========================
                    output = BytesIO()

                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        workbook = writer.book

                        # 定义格式
                        format_green = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})  # 绿
                        format_red = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})     # 红
                        format_yellow = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C0000'}) # 黄
                        format_header = workbook.add_format({'bold': True, 'bg_color': '#366092', 'font_color': 'white'})

                        # 构建对比数据
                        comparison_data = []
                        all_keys = set(df1['__key__'].tolist() + df2['__key__'].tolist())

                        for key in all_keys:
                            row_data = {'匹配字段': key}
                            f1_row = df1[df1['__key__'] == key]
                            f2_row = df2[df2['__key__'] == key]

                            # 文件1数据
                            for col in FIXED_COLUMNS:
                                val = f1_row.iloc[0][col] if not f1_row.empty else ""
                                row_data[f'文件1_{col}'] = val

                            # 文件2数据
                            for col in FIXED_COLUMNS:
                                val = f2_row.iloc[0][col] if not f2_row.empty else ""
                                row_data[f'文件2_{col}'] = val

                            # 判断状态
                            if not f1_row.empty and not f2_row.empty:
                                has_diff = False
                                for col in FIXED_COLUMNS:
                                    if col not in key_columns:
                                        v1 = str(f1_row.iloc[0][col]) if not pd.isna(f1_row.iloc[0][col]) else ""
                                        v2 = str(f2_row.iloc[0][col]) if not pd.isna(f2_row.iloc[0][col]) else ""
                                        if v1 != v2:
                                            has_diff = True
                                            break
                                row_data['对比状态'] = '字段差异' if has_diff else '数据一致'
                            elif not f1_row.empty:
                                row_data['对比状态'] = '仅文件1有'
                            else:
                                row_data['对比状态'] = '仅文件2有'

                            comparison_data.append(row_data)

                        comparison_df = pd.DataFrame(comparison_data)

                        # 重新排序列
                        file1_cols = [f'文件1_{col}' for col in FIXED_COLUMNS]
                        file2_cols = [f'文件2_{col}' for col in FIXED_COLUMNS]
                        final_cols = ['匹配字段'] + file1_cols + file2_cols + ['对比状态']
                        comparison_df = comparison_df[final_cols]

                        # 写入主表
                        comparison_df.to_excel(writer, sheet_name='精确键值对比', index=False)
                        worksheet = writer.sheets['精确键值对比']

                        # 设置列宽
                        worksheet.set_column(0, 0, 25)  # 匹配字段
                        for i in range(1, len(final_cols)-1):
                            worksheet.set_column(i, i, 18)
                        worksheet.set_column(len(final_cols)-1, len(final_cols)-1, 15)

                        # 应用颜色
                        for row_idx in range(1, len(comparison_df)+1):
                            status = comparison_df.iloc[row_idx-1]['对比状态']
                            if status == '仅文件1有':
                                worksheet.set_row(row_idx, None, format_green)
                            elif status == '仅文件2有':
                                worksheet.set_row(row_idx, None, format_red)
                            elif status == '字段差异':
                                worksheet.set_row(row_idx, None, format_yellow)

                        # 标题行格式
                        for col_num, value in enumerate(comparison_df.columns):
                            worksheet.write(0, col_num, value, format_header)

                        # 差异汇总表
                        status_counts = {
                            '数据一致': len(comparison_df[comparison_df['对比状态'] == '数据一致']),
                            '仅文件1有': len(comparison_df[comparison_df['对比状态'] == '仅文件1有']),
                            '仅文件2有': len(comparison_df[comparison_df['对比状态'] == '仅文件2有']),
                            '字段差异': len(comparison_df[comparison_df['对比状态'] == '字段差异'])
                        }

                        summary_data = {
                            '对比状态': ['数据一致', '仅文件1有', '仅文件2有', '字段差异', '文件1总行数', '文件2总行数'],
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

                        worksheet_summary = writer.sheets['差异汇总']
                        worksheet_summary.set_column(0, 0, 15)
                        worksheet_summary.set_column(1, 1, 10)
                        worksheet_summary.set_column(2, 2, 40)
                        for col_num, value in enumerate(summary_df.columns):
                            worksheet_summary.write(0, col_num, value, format_header)

                    # ========================
                    # 在网页上展示结果
                    # ========================
                    st.subheader("📊 精确对比结果")

                    st.info("""
                    **Excel报告包含2个工作表：**
                    - 🔍 **精确键值对比**：左右并排显示，带颜色标识
                    - 📈 **差异汇总**：统计信息

                    **颜色标识说明：**
                    - 🟢 浅绿色：仅出现在第一个文件
                    - 🔴 浅红色：仅出现在第二个文件  
                    - 🟡 浅黄色：字段值不同
                    """)

                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("📄 文件1总行数", len(df1))
                    col2.metric("📄 文件2总行数", len(df2))
                    col3.metric("✅ 数据一致", status_counts['数据一致'])
                    col4.metric("⚠️ 字段差异", status_counts['字段差异'])

                    # 预览
                    preview_cols = ['匹配字段'] + file1_cols[:3] + file2_cols[:3] + ['对比状态']
                    preview_df = comparison_df[preview_cols].head(10)
                    rename_dict = {c: c.replace('文件1_', '文件1.').replace('文件2_', '文件2.') for c in preview_cols}
                    preview_df = preview_df.rename(columns=rename_dict)
                    st.write("### 👀 对比结果预览")
                    st.dataframe(preview_df, use_container_width=True)

                    # 完全一致提示
                    total_diff = status_counts['仅文件1有'] + status_counts['仅文件2有'] + status_counts['字段差异']
                    if total_diff == 0:
                        st.balloons()
                        st.success("🎉 两个文件数据完全一致！")

                    # 下载按钮
                    excel_data = output.getvalue()
                    st.download_button(
                        label="📥 下载精确对比报告",
                        data=excel_data,
                        file_name=f"精确对比报告_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

    except Exception as e:
        st.error(f"❌ 处理文件时出错：{str(e)}")
        st.code(str(e), language='traceback')