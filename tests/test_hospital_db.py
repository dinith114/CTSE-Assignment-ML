from app.tools.hospital_db_tool import hospital_db_tool

def test_valid_query():
    doctors = hospital_db_tool("cardiologist", "Colombo")
    assert isinstance(doctors, list)

def test_no_results():
    doctors = hospital_db_tool("unknown", "Colombo")
    assert doctors == []

def test_case_insensitive():
    doctors = hospital_db_tool("CARDIOLOGIST", "COLOMBO")
    assert isinstance(doctors, list)