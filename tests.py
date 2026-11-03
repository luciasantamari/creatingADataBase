import pytest
from bbdd import AlphabeticalDirectory

@pytest.fixture 
def directory(tmp_path):
  
    db_path = str(tmp_path / "test_data.log")
    db = AlphabeticalDirectory(db_path)
    yield db
    db.close()


def test_insert_and_search_found(directory):
    offset = directory.insert("boat")
    
   
    assert directory.search("boat") == [offset]


def test_search_not_found(directory):
   
    assert directory.search("sail") == []


def test_delete(directory):
    offset = directory.insert("sail")
    assert directory.search("sail") == [offset]

   
    assert directory.delete("sail") is True
    assert directory.search("sail") == []
    

    assert directory.delete("sail") is False


def test_no_duplicates(directory):
    offset1 = directory.insert("boat")
    offset2 = directory.insert("boat")

    assert offset1 == offset2
    assert directory.search("boat") == [offset1]


def test_case_and_accents(directory):
    lower = directory.insert("boat")
    upper = directory.insert("Boat")
    accent = directory.insert("canción")

    
    assert directory.search("BOAT") == [lower, upper]
    assert directory.search("CANCION") == [accent]
    assert directory.search("cancion") == [accent]

  
    assert directory.search("Boat", case_sensitive=True) == [upper]
    assert directory.search("BOAT", case_sensitive=True) == []
    assert directory.search("CANCION", case_sensitive=True) == []


def test_persistence(tmp_path):
    db_path = str(tmp_path / "test_data.log")

    directory1 = AlphabeticalDirectory(db_path)
    offset = directory1.insert("boat")
    directory1.close()

 
    directory2 = AlphabeticalDirectory(db_path)
    try:
        assert directory2.search("boat") == [offset]
    finally:
        directory2.close()


def test_invalid_inputs(directory):
  
    with pytest.raises(ValueError):
        directory.insert("")
    
    with pytest.raises(TypeError):
        directory.insert(123)


def test_o1_performance(tmp_path):
    db_path = str(tmp_path / "test_data.log")
    
   
    dir_setup = AlphabeticalDirectory(db_path)
    for i in range(100):
        dir_setup.insert(f"word{i}")
    dir_setup.close()

  
    dir_indexed = AlphabeticalDirectory(db_path, use_index=True)
   
    reads_before_index_search = dir_indexed.storage.records_read
    
    result_indexed = dir_indexed.search("word99")
    
    reads_after_index_search = dir_indexed.storage.records_read
    
  
    dir_sequential = AlphabeticalDirectory(db_path, use_index=False)
  
    reads_before_seq_search = dir_sequential.storage.records_read
    
    result_sequential = dir_sequential.search("word99")
    
    reads_after_seq_search = dir_sequential.storage.records_read

  
    assert result_indexed == result_sequential, "Ambos modos deben dar el mismo resultado"
    
 
    assert reads_after_index_search - reads_before_index_search == 0
    
 
    assert reads_after_seq_search - reads_before_seq_search == 100
    dir_indexed.close()
    dir_sequential.close()