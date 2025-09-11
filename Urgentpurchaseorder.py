import streamlit as st
import pandas as pd
import requests
from io import BytesIO


def main():
    # 设置页面标题
    st.title('加急采购单 - 待到货数据')

    # 新增：直接读取GitHub仓库中的数据文件
    st.subheader("数据加载中...")
    try:
        # 注意：需要将GitHub文件链接转换为raw格式
        # 正确格式应该是：https://raw.githubusercontent.com/用户名/仓库名/分支名/文件名
        # 请根据你的实际仓库信息修改下面的URL
        data_url = "https://raw.githubusercontent.com/Jane-zzz-123/---/main/Urgentpurchaseorder.xlsx"

        # 从URL读取数据
        response = requests.get(data_url)
        response.raise_for_status()  # 检查请求是否成功

        # 将内容转换为可读取的Excel格式
        excel_data = BytesIO(response.content)

        # 只读取存在的"Sheet1"sheet
        current_data = pd.read_excel(
            excel_data,
            sheet_name="Sheet1",
            engine='openpyxl'  # 明确指定引擎
        )

        # 将读取到的数据赋值给df变量
        df = current_data

        # 显示原始数据的列名，帮助确认列名是否正确
        with st.expander("查看所有列名（用于确认）"):
            st.write("数据中的列名：")
            st.write(df.columns.tolist())

        # 检查是否有必要的列
        required_columns = ["判断是否到货", "店铺"]
        missing_required = [col for col in required_columns if col not in df.columns]
        if missing_required:
            st.error(f"数据中缺少必要的列：{', '.join(missing_required)}，请检查列名是否正确")
            return

        # 筛选出"是否到货=待到货"的数据
        filtered_df = df[df["判断是否到货"] == "待到货"]

        # 检查是否有符合条件的数据
        if filtered_df.empty:
            st.info("没有找到'判断是否到货=待到货'的数据")
            return

        # 获取所有店铺列表并排序
        all_stores = sorted(filtered_df["店铺"].unique())

        # 将筛选器放在表格上方
        st.subheader("筛选条件")
        selected_stores = st.multiselect(
            "选择店铺",
            options=all_stores,
            default=all_stores  # 默认选中所有店铺
        )

        # 根据选择的店铺筛选数据
        if selected_stores:
            filtered_by_store = filtered_df[filtered_df["店铺"].isin(selected_stores)]
        else:
            filtered_by_store = pd.DataFrame()  # 空数据框

        # 定义需要展示的列
        columns_to_display = [
            "店铺", "MSKU", "品名", "采购数量",
            "待到货数量", "预计到货时间", "物流单号"
        ]

        # 检查所需的列是否都存在
        missing_columns = [col for col in columns_to_display if col not in filtered_by_store.columns]
        if missing_columns:
            st.warning(f"以下列在数据中未找到，将不会显示：{', '.join(missing_columns)}")
            # 只保留存在的列
            columns_to_display = [col for col in columns_to_display if col in filtered_by_store.columns]

        # 显示筛选后的数据，设置use_container_width=True让表格宽度与屏幕一致
        st.subheader(f"待到货数据（共 {len(filtered_by_store)} 条）")
        if not filtered_by_store.empty:
            st.dataframe(filtered_by_store[columns_to_display], use_container_width=True)

            # 提供下载功能
            csv = filtered_by_store[columns_to_display].to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="下载当前筛选数据 (CSV)",
                data=csv,
                file_name="筛选的待到货数据.csv",
                mime="text/csv",
            )
        else:
            st.info("没有找到符合筛选条件的数据，请尝试选择其他店铺")

    except requests.exceptions.HTTPError as e:
        st.error(f"下载文件失败: 请检查URL是否正确 - {str(e)}")
    except Exception as e:
        st.error(f"处理数据时发生错误: {str(e)}")


if __name__ == "__main__":
    main()