import main

def test_get_data():
    try:
        data=main.get_gtm_version_data(main.service)
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
        data=main.get_gtm_version_data(main.service)
        print("\nTesting get_version")
        assert data is not None
        print("Testing get_data     data is not None")
        version = main.get_version(data)
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
        main.save_version_to_cloud(main.client, "test data", "test.json", "gtm-state-storage")
    except Exception as e:
        print("Test storage save failed...")
        print(e)
    try:    
        bucket = main.client.get_bucket("gtm-state-storage")
        test = bucket.get_blob("test.json")
        test_value = test.download_as_string()
        assert test_value == b"test data", "test is {test_value}" 
        print(f"Test value is successfully written as {test_value}")
    except Exception as e:
        print("Tests storage save failed...")
        print(e)

def test_cloud_storage_load():
    print("\nTesting load_version_from_cloud")
    try:
        test = main.load_version_from_cloud(main.client, "test.json", "gtm-state-storage")
        assert test == b"test data", f"test is {test}"
        print("Load version passed")
    except Exception as e:
        print("Load version failed")
        print(e)

if __name__ == "__main__":
    try:
        print("Tests started...")
        test_get_data()
        test_version()
        test_cloud_storage_save()
        test_cloud_storage_load()
    except Exception as e:
        print("Tests failed...")
        print(e)

