import streamlit as st
import pandas as pd
import numpy as np

# 页面标题
st.title("📊 BOM对比")
st.markdown("上传两个Excel文件，选择多个字段进行联合对比")

# 上传文件
file1 = st.file_uploader(" 上传【旧版本】Excel", type=["xlsx", "xls"], key="old")
file2 = st.file_uploader(" 上传【新版本】Excel", type=["xlsx", "xls"], key="new")

if file1 and file2:
    try:
        df_old = pd.read_excel(file1)
        df_new = pd.read_excel(file2)

        st.success("✅ 文件读取成功！")
        st.write("旧数据预览：")
        st.dataframe(df_old.head(3))
        st.write("新数据预览：")
        st.dataframe(df_new.head(3))

        # 选择多个主键列
        columns = df_old.columns.tolist()
        if len(columns) < 1:
            st.error("❌ 表格没有列，请检查文件")
        else:
            key_columns = st.multiselect(
                "请选择用于匹配的字段（如：名称、数量之类）",
                options=columns,
                default=columns[0]  # 默认选中第一列
            )

            if len(key_columns) == 0:
                st.warning("⚠️ 请至少选择一个匹配字段")
            else:
                if st.button("🔍 开始对比"):
                    with st.spinner("正在对比中..."):
                        # 使用多字段创建唯一键（拼接成字符串）
                        df_old['对比的字段'] = df_old[key_columns].astype(str).apply(lambda x: '｜'.join(x), axis=1)
                        df_new['对比的字段'] = df_new[key_columns].astype(str).apply(lambda x: '｜'.join(x), axis=1)

                        # 重置索引，避免重复
                        df_old = df_old.reset_index(drop=True)
                        df_new = df_new.reset_index(drop=True)

                        # 使用 merge 进行对比（支持 suffixes）
                        combined = df_old.merge(
                            df_new,
                            on='对比的字段',
                            how='outer',
                            suffixes=('_旧', '_新'),
                            indicator=True
                        )

                        # 分析差异
                        added = combined[combined['_merge'] == 'right_only']
                        deleted = combined[combined['_merge'] == 'left_only']
                        unchanged = combined[combined['_merge'] == 'both']

                        # 找出修改的行（值不同）
                        modified = combined[combined['_merge'] == 'both'].copy()
                        value_cols = [c for c in modified.columns if c.endswith('_旧') or c.endswith('_新')]
                        if value_cols:
                            old_cols = [c for c in value_cols if c.endswith('_旧')]
                            new_cols = [c.replace('_旧', '_新') for c in old_cols]
                            modified['is_changed'] = False
                            for old_col, new_col in zip(old_cols, new_cols):
                                old_val = modified[old_col].fillna('')
                                new_val = modified[new_col].fillna('')
                                modified['is_changed'] |= (old_val != new_val)
                            modified = modified[modified['is_changed']]

                        # 显示结果
                        st.subheader("📌 对比结果")

                        col1, col2, col3 = st.columns(3)
                        col1.metric("🟢 新增", len(added))
                        col2.metric("🔴 删除", len(deleted))
                        col3.metric("⚠️ 修改", len(modified))

                        if not added.empty:
                            st.write("### 🟢 新增的数据：")
                            st.dataframe(added.drop(['_merge'], axis=1, errors='ignore').reset_index(drop=True))

                        if not deleted.empty:
                            st.write("### 🔴 删除的数据：")
                            st.dataframe(deleted.drop(['_merge'], axis=1, errors='ignore').reset_index(drop=True))

                        if not modified.empty:
                            st.write("### ⚠️ 修改的数据（显示新旧对比）：")
                            st.dataframe(
                                modified.drop(['_merge', 'is_changed'], axis=1, errors='ignore').reset_index(drop=True))

                        if len(added) == 0 and len(deleted) == 0 and len(modified) == 0:
                            st.balloons()
                            st.success("🎉 两个文件完全一致，无差异！")

    except Exception as e:
        st.error(f"❌ 处理文件时出错：{str(e)}")