import check_version

def test_get_data():
    try:
        data=check_version.get_gtm_version_data(check_version.service)
        print("\nTesting get_data")
        assert data is not None
        print("Testing get_data     data is not None")
        assert len(data) > 0
        print("Testing get_data     data len > 0")
        print("Get data passed")
    except Exception as e:
        print(e)

def test_version():
    try:
        data=check_version.get_gtm_version_data(check_version.service)
        print("\nTesting get_version")
        assert data is not None
        print("Testing get_data     data is not None")
        version = check_version.get_version(data)
        assert len(version) > 0
        print("Testing get_version    version len > 0")
        assert type(version) == str
        print("Testing get_version    version is string")
        print("Get version passed")
    except Exception as e:
        print("Test version Failed")
        print(e)

if __name__ == "__main__":
    print("Tests started...")
    test_get_data()
    test_version()

