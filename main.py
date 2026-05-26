#!/usr/bin/env python3
"""API Service - FastAPI RESTful 接口服务"""

from typing import Optional
from io import StringIO

import pandas as pd
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI(title="API Service", description="轻量级 RESTful 接口服务", version="1.0.0")

# 示例数据
SAMPLE_DATA = [
    {"id": 1, "name": "张三", "age": 28, "city": "北京", "salary": 15000},
    {"id": 2, "name": "李四", "age": 32, "city": "上海", "salary": 18000},
    {"id": 3, "name": "王五", "age": 25, "city": "广州", "salary": 12000},
    {"id": 4, "name": "赵六", "age": 35, "city": "深圳", "salary": 22000},
    {"id": 5, "name": "钱七", "age": 29, "city": "杭州", "salary": 16000},
    {"id": 6, "name": "孙八", "age": 31, "city": "成都", "salary": 14000},
    {"id": 7, "name": "周九", "age": 27, "city": "武汉", "salary": 13000},
    {"id": 8, "name": "吴十", "age": 33, "city": "南京", "salary": 17000},
]


@app.get("/")
def root():
    return {"message": "API Service 运行中", "docs": "/docs"}


@app.get("/api/data")
def get_data(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    city: Optional[str] = Query(None, description="按城市筛选"),
    sort_by: Optional[str] = Query(None, description="排序字段"),
):
    """查询数据（支持分页和筛选）"""
    df = pd.DataFrame(SAMPLE_DATA)

    if city:
        df = df[df["city"].str.contains(city, na=False)]

    if sort_by and sort_by in df.columns:
        df = df.sort_values(sort_by)

    total = len(df)
    start = (page - 1) * size
    end = start + size
    records = df.iloc[start:end].to_dict(orient="records")

    return {"total": total, "page": page, "size": size, "data": records}


@app.get("/api/export")
def export_data(format: str = Query("json", regex="^(json|csv)$", description="导出格式")):
    """导出数据（JSON / CSV）"""
    df = pd.DataFrame(SAMPLE_DATA)

    if format == "csv":
        output = StringIO()
        df.to_csv(output, index=False, encoding="utf-8-sig")
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=data.csv"},
        )

    return {"data": df.to_dict(orient="records")}


@app.get("/api/stats")
def stats():
    """数据统计"""
    df = pd.DataFrame(SAMPLE_DATA)
    return {
        "total": len(df),
        "avg_age": round(df["age"].mean(), 1),
        "avg_salary": round(df["salary"].mean(), 1),
        "cities": df["city"].value_counts().to_dict(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
