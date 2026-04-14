import pytest
import requests
import json

# vesp-gvs-vehicle 服务测试

def test_0205fd62():
    """positive_0205fd62"""
    url = f"http://localhost:8080/api/v1/admin/{modelId}/images/{type}/extend"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_19c86363():
    """positive_19c86363"""
    url = f"http://localhost:8080/api/v1/manifests"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_19c86363():
    """positive_19c86363"""
    url = f"http://localhost:8080/api/v1/manifests"
    payload = {}

    response = requests.post(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_6715813c():
    """positive_6715813c"""
    url = f"http://localhost:8080/api/v1/manifests/{id}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_6715813c():
    """positive_6715813c"""
    url = f"http://localhost:8080/api/v1/manifests/{id}"
    payload = {}

    response = requests.put(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_cd76cf6d():
    """positive_cd76cf6d"""
    url = f"http://localhost:8080/api/v1/manifests/{id}/action/restore"
    payload = {}

    response = requests.put(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_5b76ac2a():
    """positive_5b76ac2a"""
    url = f"http://localhost:8080/api/v1/manifests/{vin}/latest"
    payload = {}

    response = requests.post(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_1043accd():
    """positive_1043accd"""
    url = f"http://localhost:8080/api/v1/vehicles/{vin}/images/{type}/extend"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_d3e8f443():
    """positive_d3e8f443"""
    url = f"http://localhost:8080/api/v2/admin/brand/models/codes"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_deb512c8():
    """positive_deb512c8"""
    url = f"http://localhost:8080/api/v2/admin/brand/year/modelInfo"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_eb49433f():
    """positive_eb49433f"""
    url = f"http://localhost:8080/api/v2/admin/brand/years"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_ebd70f78():
    """positive_ebd70f78"""
    url = f"http://localhost:8080/api/v2/admin/models/{modelId}/colors"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_2186ad18():
    """positive_2186ad18"""
    url = f"http://localhost:8080/api/v2/admin/vehicles/summarise"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_b9ce97b6():
    """positive_b9ce97b6"""
    url = f"http://localhost:8080/api/v2/after-vicp-device/vehicles/{vin}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_b0229bfd():
    """positive_b0229bfd"""
    url = f"http://localhost:8080/api/v2/brand/{brandCode}/platforms"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_24ff8cb5():
    """positive_24ff8cb5"""
    url = f"http://localhost:8080/api/v2/brand/{brandId}/series"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_460fc93d():
    """positive_460fc93d"""
    url = f"http://localhost:8080/api/v2/brands/{brandCode}/vehicles/sims/{iccid}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_0e201490():
    """positive_0e201490"""
    url = f"http://localhost:8080/api/v2/brands/{brand}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_f011a002():
    """positive_f011a002"""
    url = f"http://localhost:8080/api/v2/cache/{key}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_afaff24e():
    """positive_afaff24e"""
    url = f"http://localhost:8080/api/v2/capabilities"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_0b830494():
    """positive_0b830494"""
    url = f"http://localhost:8080/api/v2/capabilities/{id}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_0b830494():
    """positive_0b830494"""
    url = f"http://localhost:8080/api/v2/capabilities/{id}"
    payload = {}

    response = requests.delete(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_1c4ad9a9():
    """positive_1c4ad9a9"""
    url = f"http://localhost:8080/api/v2/capability-categories"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_97a28938():
    """positive_97a28938"""
    url = f"http://localhost:8080/api/v2/capability-categories/{id}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_40ea7bbf():
    """positive_40ea7bbf"""
    url = f"http://localhost:8080/api/v2/capability-operations"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_21f4f234():
    """positive_21f4f234"""
    url = f"http://localhost:8080/api/v2/devices"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_683fb5cf():
    """positive_683fb5cf"""
    url = f"http://localhost:8080/api/v2/devices/{id}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_683fb5cf():
    """positive_683fb5cf"""
    url = f"http://localhost:8080/api/v2/devices/{id}"
    payload = {}

    response = requests.delete(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_147eba98():
    """positive_147eba98"""
    url = f"http://localhost:8080/api/v2/function-on-demand"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_dd27e3a8():
    """positive_dd27e3a8"""
    url = f"http://localhost:8080/api/v2/function-on-demand/{id}"
    payload = {}

    response = requests.delete(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_03ae43cd():
    """positive_03ae43cd"""
    url = f"http://localhost:8080/api/v2/hu/history"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_1a431e18():
    """positive_1a431e18"""
    url = f"http://localhost:8080/api/v2/hu/history/docs"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_a741a272():
    """positive_a741a272"""
    url = f"http://localhost:8080/api/v2/model-metadata"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_50d5d1c7():
    """positive_50d5d1c7"""
    url = f"http://localhost:8080/api/v2/model/dynamic-package"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_4bd02843():
    """positive_4bd02843"""
    url = f"http://localhost:8080/api/v2/model/dynamic-package/hold"
    payload = {}

    response = requests.post(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_dd3475cc():
    """positive_dd3475cc"""
    url = f"http://localhost:8080/api/v2/model/dynamic-package/reset"
    payload = {}

    response = requests.post(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_37c96deb():
    """positive_37c96deb"""
    url = f"http://localhost:8080/api/v2/model/lineNo/{brand}/{lineNo}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_9a61af9a():
    """positive_9a61af9a"""
    url = f"http://localhost:8080/api/v2/models"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_06bba375():
    """positive_06bba375"""
    url = f"http://localhost:8080/api/v2/models/brand/{brand}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_c4436d97():
    """positive_c4436d97"""
    url = f"http://localhost:8080/api/v2/models/colors/image-unmaintained"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_398f1e1c():
    """positive_398f1e1c"""
    url = f"http://localhost:8080/api/v2/models/types"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_0a1e26b3():
    """positive_0a1e26b3"""
    url = f"http://localhost:8080/api/v2/models/{id}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_c3132eb6():
    """positive_c3132eb6"""
    url = f"http://localhost:8080/api/v2/models/{modelId}/capabilities"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_406875a5():
    """positive_406875a5"""
    url = f"http://localhost:8080/api/v2/models/{modelId}/operation-histories"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_6658bbf9():
    """positive_6658bbf9"""
    url = f"http://localhost:8080/api/v2/operations/{vin}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_393c26d8():
    """positive_393c26d8"""
    url = f"http://localhost:8080/api/v2/optional-part/{id}"
    payload = {}

    response = requests.delete(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_3f3b9a1c():
    """positive_3f3b9a1c"""
    url = f"http://localhost:8080/api/v2/optional-parts"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_186a082f():
    """positive_186a082f"""
    url = f"http://localhost:8080/api/v2/optional-parts/{id}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_9f8157d9():
    """positive_9f8157d9"""
    url = f"http://localhost:8080/api/v2/platform-version/configuration"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_2268d986():
    """positive_2268d986"""
    url = f"http://localhost:8080/api/v2/platform-version/configuration/{id}"
    payload = {}

    response = requests.delete(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_d36949c9():
    """positive_d36949c9"""
    url = f"http://localhost:8080/api/v2/qcode"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_c8893677():
    """positive_c8893677"""
    url = f"http://localhost:8080/api/v2/series/brands/{brand}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_59b15370():
    """positive_59b15370"""
    url = f"http://localhost:8080/api/v2/series/info"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_f481c110():
    """positive_f481c110"""
    url = f"http://localhost:8080/api/v2/sims"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_3a61033f():
    """positive_3a61033f"""
    url = f"http://localhost:8080/api/v2/sims/carriers"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_d7a8e497():
    """positive_d7a8e497"""
    url = f"http://localhost:8080/api/v2/sims/compensationVehicleCellular"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_27eb323d():
    """positive_27eb323d"""
    url = f"http://localhost:8080/api/v2/sims/{id}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_27eb323d():
    """positive_27eb323d"""
    url = f"http://localhost:8080/api/v2/sims/{id}"
    payload = {}

    response = requests.delete(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_e7eab1f1():
    """positive_e7eab1f1"""
    url = f"http://localhost:8080/api/v2/sims/{msisdn}/vehicles"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_ca06b48b():
    """positive_ca06b48b"""
    url = f"http://localhost:8080/api/v2/software-version/configuration"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_a5a82681():
    """positive_a5a82681"""
    url = f"http://localhost:8080/api/v2/software-version/configuration/{id}"
    payload = {}

    response = requests.delete(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_970ac86b():
    """positive_970ac86b"""
    url = f"http://localhost:8080/api/v2/tags"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_77eb38b2():
    """positive_77eb38b2"""
    url = f"http://localhost:8080/api/v2/tags/{id}"
    payload = {}

    response = requests.delete(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_9b44375b():
    """positive_9b44375b"""
    url = f"http://localhost:8080/api/v2/tags/{tagId}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_7ae488d3():
    """positive_7ae488d3"""
    url = f"http://localhost:8080/api/v2/users/vehicles/{vin}/wifiStickStatus"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_54ddec9f():
    """positive_54ddec9f"""
    url = f"http://localhost:8080/api/v2/vehicle/devices/ocus/siminfo"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_7da787c7():
    """positive_7da787c7"""
    url = f"http://localhost:8080/api/v2/vehicle/model/action/reselect"
    payload = {}

    response = requests.post(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_8c6017eb():
    """positive_8c6017eb"""
    url = f"http://localhost:8080/api/v2/vehicles"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_d7ec4c6a():
    """positive_d7ec4c6a"""
    url = f"http://localhost:8080/api/v2/vehicles/devices/manufactures"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_e200cdbb():
    """positive_e200cdbb"""
    url = f"http://localhost:8080/api/v2/vehicles/devices/ocu/download"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_86f43d50():
    """positive_86f43d50"""
    url = f"http://localhost:8080/api/v2/vehicles/devices/ocu/download/data"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_61270ab3():
    """positive_61270ab3"""
    url = f"http://localhost:8080/api/v2/vehicles/devices/ocu/history"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_91936b00():
    """positive_91936b00"""
    url = f"http://localhost:8080/api/v2/vehicles/devices/ocu/import"
    payload = {}

    response = requests.post(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_dc325884():
    """positive_dc325884"""
    url = f"http://localhost:8080/api/v2/vehicles/devices/ocu/importVin"
    payload = {}

    response = requests.post(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_fe4c9e0a():
    """positive_fe4c9e0a"""
    url = f"http://localhost:8080/api/v2/vehicles/devices/ocu/list"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_006c54c9():
    """positive_006c54c9"""
    url = f"http://localhost:8080/api/v2/vehicles/devices/platform-version/import"
    payload = {}

    response = requests.post(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_b1a2cfbd():
    """positive_b1a2cfbd"""
    url = f"http://localhost:8080/api/v2/vehicles/devices/{deviceSn}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_203dadf4():
    """positive_203dadf4"""
    url = f"http://localhost:8080/api/v2/vehicles/partial-info/{vin}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_5aea3715():
    """positive_5aea3715"""
    url = f"http://localhost:8080/api/v2/vehicles/platform-version"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_365d77ae():
    """positive_365d77ae"""
    url = f"http://localhost:8080/api/v2/vehicles/{id}"
    payload = {}

    response = requests.delete(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_aba1a15d():
    """positive_aba1a15d"""
    url = f"http://localhost:8080/api/v2/vehicles/{vehicle_id}/device-type/{device_type}/history"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_175b2753():
    """positive_175b2753"""
    url = f"http://localhost:8080/api/v2/vehicles/{vins}/edit/tags"
    payload = {}

    response = requests.delete(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_739d6cd0():
    """positive_739d6cd0"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_1f57f6a2():
    """positive_1f57f6a2"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/capabilities"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_ee139d5b():
    """positive_ee139d5b"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/devices"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_7159b03c():
    """positive_7159b03c"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/devices/cdi"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_c273d8fb():
    """positive_c273d8fb"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/devices/headunits"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_0fe49c6d():
    """positive_0fe49c6d"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/devices/ocus"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_509307a1():
    """positive_509307a1"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/devices/ocus/sims"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_a38fcd58():
    """positive_a38fcd58"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/devices/ocus/sims/{iccid}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_cbd18a8f():
    """positive_cbd18a8f"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/devices/ocus/{deviceId}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_62c7d958():
    """positive_62c7d958"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/devices/part-no"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_027611fd():
    """positive_027611fd"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/function-on-demand"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_eb75b782():
    """positive_eb75b782"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/function-on-demand/{serviceId}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_8c0bbe62():
    """positive_8c0bbe62"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/hand-book"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_d1d03959():
    """positive_d1d03959"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/images"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_0e753433():
    """positive_0e753433"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/importer-no"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_274785cd():
    """positive_274785cd"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/model"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_b50afbdc():
    """positive_b50afbdc"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/platform-version"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_b50afbdc():
    """positive_b50afbdc"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/platform-version"
    payload = {}

    response = requests.delete(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_74f8d0c1():
    """positive_74f8d0c1"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/quality-cert"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_a2ae24a4():
    """positive_a2ae24a4"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/real-name"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_c0b93d07():
    """positive_c0b93d07"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/software-version/{software}"
    payload = {}

    response = requests.post(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_ac85c91a():
    """positive_ac85c91a"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/ticket-system"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_8cb92b75():
    """positive_8cb92b75"""
    url = f"http://localhost:8080/api/v2/vehicles/{vin}/vehicle-data"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_56251f8e():
    """positive_56251f8e"""
    url = f"http://localhost:8080/api/v3/test/vehicle/model/amend"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_e1073c53():
    """positive_e1073c53"""
    url = f"http://localhost:8080/api/v3/test/vehicle/model/realign"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_f9458764():
    """positive_f9458764"""
    url = f"http://localhost:8080/api/v3/test/vehicle/model/{modelId}/deleted"
    payload = {}

    response = requests.put(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_5201bcb1():
    """positive_5201bcb1"""
    url = f"http://localhost:8080/api/v3/vehicles/devices/{deviceSn}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_cd5a4717():
    """positive_cd5a4717"""
    url = f"http://localhost:8080/api/v3/vehicles/images"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_f27b6fa7():
    """positive_f27b6fa7"""
    url = f"http://localhost:8080/api/v3/vehicles/{vin}"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_64ba86b2():
    """positive_64ba86b2"""
    url = f"http://localhost:8080/api/v3/vehicles/{vin}/brand"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_ea22ec86():
    """positive_ea22ec86"""
    url = f"http://localhost:8080/api/v3/vehicles/{vin}/devices/ocus/sims"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_c7b02edb():
    """positive_c7b02edb"""
    url = f"http://localhost:8080/api/v3/vehicles/{vin}/feature"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


def test_4ea615f0():
    """positive_4ea615f0"""
    url = f"http://localhost:8080/api/v3/vehicles/{vin}/images"
    payload = {}

    response = requests.get(
        url, 
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )

    # 状态码断言
    assert response.status_code == 200, \
        f"预期状态码 200，实际状态码 {response.status_code}"

    # 响应体验证
    if response.status_code == 200:
        response_data = response.json()
        # 添加更多的响应验证逻辑

    # 性能断言（可选）
    assert response.elapsed.total_seconds() < 2.0, "响应时间超过2秒"


