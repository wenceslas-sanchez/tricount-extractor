import json
import pathlib
from typing import Annotated

import httpx
import pandas as pd
import pytest

from tricount_extractor.main import Processor


@pytest.fixture
def test_data_dir() -> pathlib.Path:
    return pathlib.Path(__file__).parent / "data"


@pytest.fixture
def responses_dir(
    test_data_dir: Annotated[pathlib.Path, pytest.fixture],
) -> pathlib.Path:
    return test_data_dir / "responses"


@pytest.fixture
def reference_excel_dir(
    test_data_dir: Annotated[pathlib.Path, pytest.fixture],
) -> pathlib.Path:
    return test_data_dir / "expected_results"


@pytest.fixture
def auth_response() -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "Response": [
                {"Token": {"token": "test-token"}},
                {"UserPerson": {"id": "test-user-id"}},
            ]
        },
    )


@pytest.fixture
def basic_registry_data(responses_dir: Annotated[pathlib.Path, pytest.fixture]) -> dict:
    with open(responses_dir / "basic_registries.json") as f:
        return json.load(f)


@pytest.fixture
def registries_with_reimbursement_data(
    responses_dir: Annotated[pathlib.Path, pytest.fixture],
):
    with open(responses_dir / "registries_with_reimboursement.json") as f:
        return json.load(f)


@pytest.fixture
def unequal_registries_data(
    responses_dir: Annotated[pathlib.Path, pytest.fixture],
) -> dict:
    with open(responses_dir / "unequal_registries.json") as f:
        return json.load(f)


@pytest.fixture
def no_registries_data(responses_dir: Annotated[pathlib.Path, pytest.fixture]) -> dict:
    with open(responses_dir / "no_registries.json") as f:
        return json.load(f)


@pytest.fixture
def transport_single_success(auth_response, basic_registry_data):
    def handler(request):
        if "session-registry-installation" in str(request.url):
            return auth_response
        return httpx.Response(200, json=basic_registry_data)

    return httpx.MockTransport(handler)


@pytest.fixture
def transport_multiple_success(
    auth_response, basic_registry_data, registries_with_reimbursement_data
):
    registry_call_count = [0]

    def handler(request):
        if "session-registry-installation" in str(request.url):
            return auth_response
        registry_call_count[0] += 1
        if registry_call_count[0] == 1:
            return httpx.Response(200, json=basic_registry_data)
        return httpx.Response(200, json=registries_with_reimbursement_data)

    return httpx.MockTransport(handler)


@pytest.fixture
def transport_partial_failure(auth_response, basic_registry_data):
    registry_call_count = [0]

    def handler(request):
        if "session-registry-installation" in str(request.url):
            return auth_response
        registry_call_count[0] += 1
        if registry_call_count[0] == 1:
            return httpx.Response(200, json=basic_registry_data)
        return httpx.Response(404, json={"error": "Not found"})

    return httpx.MockTransport(handler)


@pytest.fixture
def transport_all_failures(auth_response):
    def handler(request):
        if "session-registry-installation" in str(request.url):
            return auth_response
        return httpx.Response(404, json={"error": "Not found"})

    return httpx.MockTransport(handler)


@pytest.fixture
def transport_unequal_registries(auth_response, unequal_registries_data):
    def handler(request):
        if "session-registry-installation" in str(request.url):
            return auth_response
        return httpx.Response(200, json=unequal_registries_data)

    return httpx.MockTransport(handler)


@pytest.fixture
def transport_no_registries(auth_response, no_registries_data):
    def handler(request):
        if "session-registry-installation" in str(request.url):
            return auth_response
        return httpx.Response(200, json=no_registries_data)

    return httpx.MockTransport(handler)


def compare_excel_files(generated_path: pathlib.Path, reference_path: pathlib.Path):
    generated_excel = pd.ExcelFile(generated_path)
    reference_excel = pd.ExcelFile(reference_path)

    assert generated_excel.sheet_names == reference_excel.sheet_names

    for sheet_name in generated_excel.sheet_names:
        generated_df = pd.read_excel(generated_path, sheet_name=sheet_name, index_col=0)
        reference_df = pd.read_excel(reference_path, sheet_name=sheet_name, index_col=0)
        pd.testing.assert_frame_equal(generated_df, reference_df)


def test_process_single_registry_successfully(
    transport_single_success, tmp_path, reference_excel_dir
):
    processor = Processor()
    processor.process(["reg-001"], str(tmp_path), transport=transport_single_success)

    saved_files = list(tmp_path.glob("*.xlsx"))
    assert len(saved_files) == 1

    generated_file = saved_files[0]
    compare_excel_files(generated_file, reference_excel_dir / "test_trip_1.xlsx")


def test_process_multiple_registries_successfully(
    transport_multiple_success, tmp_path, reference_excel_dir
):
    processor = Processor()
    processor.process(
        ["reg-001", "reg-002"], str(tmp_path), transport=transport_multiple_success
    )

    saved_files = sorted(tmp_path.glob("*.xlsx"))
    assert len(saved_files) == 2

    for generated_file in saved_files:
        reference_file = reference_excel_dir / generated_file.name
        compare_excel_files(generated_file, reference_file)


def test_process_partial_failure_raises_exception_group(
    transport_partial_failure, tmp_path, reference_excel_dir
):
    processor = Processor()

    with pytest.raises(ExceptionGroup) as exc_info:
        processor.process(
            ["reg-001", "reg-002"], str(tmp_path), transport=transport_partial_failure
        )

    assert len(exc_info.value.exceptions) == 1
    assert "reg-002" in str(exc_info.value.exceptions[0])

    saved_files = list(tmp_path.glob("*.xlsx"))
    assert len(saved_files) == 1

    generated_file = saved_files[0]
    compare_excel_files(generated_file, reference_excel_dir / "test_trip_1.xlsx")


def test_process_all_failures_raises_exception_group(transport_all_failures, tmp_path):
    processor = Processor()

    with pytest.raises(ExceptionGroup) as exc_info:
        processor.process(
            ["reg-001", "reg-002"], str(tmp_path), transport=transport_all_failures
        )

    assert len(exc_info.value.exceptions) == 2

    saved_files = list(tmp_path.glob("*.xlsx"))
    assert len(saved_files) == 0


def test_process_empty_registry_list(transport_single_success, tmp_path):
    processor = Processor()
    processor.process([], str(tmp_path), transport=transport_single_success)

    saved_files = list(tmp_path.glob("*.xlsx"))
    assert len(saved_files) == 0


def test_process_unequal_registries_successfully(
    transport_unequal_registries, tmp_path, reference_excel_dir
):
    processor = Processor()
    processor.process(
        ["reg-003"], str(tmp_path), transport=transport_unequal_registries
    )

    saved_files = list(tmp_path.glob("*.xlsx"))
    assert len(saved_files) == 1

    generated_file = saved_files[0]
    compare_excel_files(generated_file, reference_excel_dir / "dinner_group_3.xlsx")


def test_process_no_registries_raises_error(transport_no_registries, tmp_path):
    processor = Processor()

    with pytest.raises(ExceptionGroup) as exc_info:
        processor.process(["reg-000"], str(tmp_path), transport=transport_no_registries)

    assert len(exc_info.value.exceptions) == 1
    assert "reg-000" in str(exc_info.value.exceptions[0])

    saved_files = list(tmp_path.glob("*.xlsx"))
    assert len(saved_files) == 0
