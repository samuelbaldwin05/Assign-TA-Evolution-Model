from assignta import Objectives
import pandas as pd
import numpy as np
import pytest

@pytest.fixture
def obj():
    tas = pd.read_csv("tas.csv")
    sections = pd.read_csv("sections.csv")
    obj = Objectives(sections, tas)
    return obj

@pytest.fixture
def test1():
    test_data1 = np.loadtxt('test1.csv', delimiter=',')
    return test_data1

@pytest.fixture
def test2():
    test_data2 = np.loadtxt('test2.csv', delimiter=',')
    return test_data2

@pytest.fixture
def test3():
    test_data3 = np.loadtxt('test3.csv', delimiter=',')
    return test_data3

def test_overallocate(obj, test1, test2, test3):
    assert obj.overallocate(test1) == 37
    assert obj.overallocate(test2) == 41
    assert obj.overallocate(test3) == 23

def test_conflicted_sections(test1, test2, test3, obj):
    assert obj.conflicted_sections(test1) == 8
    assert obj.conflicted_sections(test2) == 5
    assert obj.conflicted_sections(test3) == 2

def test_undersupport(test1, test2, test3, obj):
    assert obj.undersupport(test1) == 1
    assert obj.undersupport(test2) == 0
    assert obj.undersupport(test3) == 7

def test_unwilling(test1, test2, test3, obj):
    assert obj.unwilling(test1) == 53
    assert obj.unwilling(test2) == 58
    assert obj.unwilling(test3) == 43

def test_unpreferred(test1, test2, test3, obj):
    assert obj.unpreferred(test1) == 15
    assert obj.unpreferred(test2) == 19
    assert obj.unpreferred(test3) == 10
