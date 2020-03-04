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

def test_cloud_storage_save():
    print("\nTesting save_version_to_cloud")
    try:
        check_version.save_version_to_cloud(check_version.client, "test data", "test.json", "gtm-state-storage")
    except Exception as e:
        print("Test storage save failed...")
        print(e)
    try:    
        bucket = check_version.client.get_bucket("gtm-state-storage")
        test = bucket.get_blob("test.json")
        test_value = test.download_as_string()
        assert test_value == b"test data", "test is {test_value}" 
        print(f"Test value is successfully written as {test_value}")
    except Exception as e:
        print("Tests storage save failed...")
        print(e)

if __name__ == "__main__":
    try:
        print("Tests started...")
        # test_get_data()
        # test_version()
        test_cloud_storage_save()
    except Exception as e:
        print("Tests failed...")
        print(e)

