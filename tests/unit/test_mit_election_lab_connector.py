# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2024 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
# SPDX-License-Identifier: Apache-2.0

"""
Contract tests for MITElectionLabConnector.

Layer 8: Contract Testing - Type validation and basic interface contracts.

These tests ensure the connector meets the interface contract defined by BaseConnector
and returns data in expected formats. They DO NOT validate data accuracy or business logic.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List

from krl_data_connectors.political.mit_election_lab_connector import MITElectionLabConnector


class TestMITElectionLabConnectorContracts:
    """Contract tests verifying MITElectionLabConnector interface compliance."""
    
    @pytest.fixture
    def connector(self):
        """Create connector instance for testing."""
        return MITElectionLabConnector()
    
    @pytest.fixture
    def sample_presidential_data(self, tmp_path):
        """Create sample presidential election CSV data."""
        csv_path = tmp_path / "test_presidential.csv"
        csv_path.write_text(
            "year,state,state_po,state_fips,state_cen,state_ic,office,candidate,party_detailed,party_simplified,"
            "mode,candidatevotes,totalvotes,writein,version\n"
            "2020,Pennsylvania,PA,42,23,62,PRESIDENT,Joe Biden,DEMOCRAT,DEMOCRAT,total,3458229,6915283,FALSE,20210113\n"
            "2020,Pennsylvania,PA,42,23,62,PRESIDENT,Donald Trump,REPUBLICAN,REPUBLICAN,total,3377674,6915283,FALSE,20210113\n"
            "2020,Pennsylvania,PA,42,23,62,PRESIDENT,Jo Jorgensen,LIBERTARIAN,OTHER,total,79380,6915283,FALSE,20210113\n"
            "2020,Georgia,GA,13,58,31,PRESIDENT,Joe Biden,DEMOCRAT,DEMOCRAT,total,2473633,4999960,FALSE,20210113\n"
            "2020,Georgia,GA,13,58,31,PRESIDENT,Donald Trump,REPUBLICAN,REPUBLICAN,total,2461854,4999960,FALSE,20210113\n"
            "2020,Georgia,GA,13,58,31,PRESIDENT,Jo Jorgensen,LIBERTARIAN,OTHER,total,62229,4999960,FALSE,20210113\n"
            "2016,Pennsylvania,PA,42,23,62,PRESIDENT,Hillary Clinton,DEMOCRAT,DEMOCRAT,total,2926441,6165478,FALSE,20210113\n"
            "2016,Pennsylvania,PA,42,23,62,PRESIDENT,Donald Trump,REPUBLICAN,REPUBLICAN,total,2970733,6165478,FALSE,20210113\n"
        )
        return csv_path
    
    @pytest.fixture
    def sample_county_data(self, tmp_path):
        """Create sample county presidential election CSV data."""
        csv_path = tmp_path / "test_county.csv"
        csv_path.write_text(
            "year,state,state_po,county_name,county_fips,office,candidate,party,candidatevotes,totalvotes,mode\n"
            "2020,Pennsylvania,PA,Philadelphia County,42101,PRESIDENT,Joe Biden,DEMOCRAT,604175,749149,total\n"
            "2020,Pennsylvania,PA,Philadelphia County,42101,PRESIDENT,Donald Trump,REPUBLICAN,132870,749149,total\n"
            "2020,Pennsylvania,PA,Allegheny County,42003,PRESIDENT,Joe Biden,DEMOCRAT,429274,681522,total\n"
            "2020,Pennsylvania,PA,Allegheny County,42003,PRESIDENT,Donald Trump,REPUBLICAN,235862,681522,total\n"
        )
        return csv_path
    
    def test_connect_return_type(self, connector):
        """
        Verify connect() returns None and doesn't raise unexpected errors.
        
        Contract: connect() should complete successfully and return None.
        Layer 8: Contract testing - interface validation.
        """
        result = connector.connect()
        assert result is None, "connect() should return None"
    
    def test_load_presidential_data_return_type(
        self,
        connector,
        sample_presidential_data
    ):
        """
        Verify load_presidential_data() returns DataFrame with correct structure.
        
        Contract: load_presidential_data() should return pandas DataFrame with
        expected columns when given valid CSV file.
        
        Layer 8: Contract testing - return type validation.
        """
        connector.connect()
        result = connector.load_presidential_data(sample_presidential_data)
        
        # Verify return type
        assert isinstance(result, pd.DataFrame), "Should return DataFrame"
        
        # Verify expected columns exist
        expected_columns = [
            'year', 'state', 'state_po', 'office', 'candidate',
            'party_simplified', 'candidatevotes', 'totalvotes'
        ]
        for col in expected_columns:
            assert col in result.columns, f"Missing expected column: {col}"
        
        # Verify data loaded
        assert len(result) == 8, "Should load 8 test records"
    
    def test_load_county_presidential_data_return_type(
        self,
        connector,
        sample_county_data
    ):
        """
        Verify load_county_presidential_data() returns DataFrame.
        
        Contract: load_county_presidential_data() should return DataFrame with
        county-level election data.
        
        Layer 8: Contract testing - method interface validation.
        """
        connector.connect()
        result = connector.load_county_presidential_data(sample_county_data)
        
        assert isinstance(result, pd.DataFrame), "Should return DataFrame"
        
        # Verify key columns
        expected_columns = [
            'year', 'state_po', 'county_name', 'county_fips',
            'candidate', 'party', 'candidatevotes', 'totalvotes'
        ]
        for col in expected_columns:
            assert col in result.columns, f"Missing expected column: {col}"
        
        assert len(result) == 4, "Should load 4 county records"
        assert result['county_fips'].dtype == 'object', "county_fips should be string"
    
    def test_get_election_results_return_type(
        self,
        connector,
        sample_presidential_data
    ):
        """
        Verify get_election_results() returns filtered DataFrame.
        
        Contract: get_election_results() should return DataFrame with
        results for specified year and office.
        
        Layer 8: Contract testing - query interface validation.
        """
        connector.connect()
        connector.load_presidential_data(sample_presidential_data)
        
        # Test year filtering
        result = connector.get_election_results(year=2020, office='president')
        
        assert isinstance(result, pd.DataFrame), "Should return DataFrame"
        assert all(result['year'] == 2020), "All records should be from 2020"
        assert len(result) == 6, "Should return 6 records for 2020"
        
        # Test state filtering
        result_pa = connector.get_election_results(year=2020, office='president', state='PA')
        assert all(result_pa['state_po'] == 'PA'), "All records should be for PA"
        assert len(result_pa) == 3, "Should return 3 PA records"
    
    def test_get_state_winner_return_type(
        self,
        connector,
        sample_presidential_data
    ):
        """
        Verify get_state_winner() returns Dict with winner information.
        
        Contract: get_state_winner() should return dictionary with
        winner name, party, votes, and margin.
        
        Layer 8: Contract testing - aggregation output validation.
        """
        connector.connect()
        connector.load_presidential_data(sample_presidential_data)
        
        result = connector.get_state_winner(year=2020, state='PA')
        
        assert isinstance(result, dict), "Should return dictionary"
        
        # Verify expected keys
        expected_keys = ['winner', 'party', 'votes', 'total_votes', 'vote_share', 'margin']
        for key in expected_keys:
            assert key in result, f"Missing expected key: {key}"
        
        # Verify types
        assert isinstance(result['winner'], str), "Winner should be string"
        assert isinstance(result['party'], str), "Party should be string"
        assert isinstance(result['votes'], int), "Votes should be int"
        assert isinstance(result['total_votes'], int), "Total votes should be int"
        assert isinstance(result['vote_share'], float), "Vote share should be float"
        assert isinstance(result['margin'], float), "Margin should be float"
        
        # Verify PA 2020 winner (Biden)
        assert result['winner'] == 'Joe Biden', "Biden should win PA 2020"
        assert result['party'] == 'DEMOCRAT', "Winner should be Democrat"
        assert result['vote_share'] > 50.0, "Winner should have >50% in this test"
    
    def test_get_swing_states_return_type(
        self,
        connector,
        sample_presidential_data
    ):
        """
        Verify get_swing_states() returns DataFrame with swing state data.
        
        Contract: get_swing_states() should return DataFrame of states
        with victory margins below threshold.
        
        Layer 8: Contract testing - threshold filtering validation.
        """
        connector.connect()
        connector.load_presidential_data(sample_presidential_data)
        
        result = connector.get_swing_states(year=2020, threshold=5.0)
        
        assert isinstance(result, pd.DataFrame), "Should return DataFrame"
        
        # Verify expected columns
        expected_columns = ['state_po', 'winner', 'party', 'margin', 'vote_share']
        for col in expected_columns:
            assert col in result.columns, f"Missing expected column: {col}"
        
        # Verify all margins meet threshold
        assert all(result['margin'] <= 5.0), "All margins should be ≤5%"
        
        # Verify sorted by margin
        margins = result['margin'].tolist()
        assert margins == sorted(margins), "Should be sorted by margin ascending"
    
    def test_get_state_trends_return_type(
        self,
        connector,
        sample_presidential_data
    ):
        """
        Verify get_state_trends() returns time series DataFrame.
        
        Contract: get_state_trends() should return DataFrame with
        electoral metrics over time for a state.
        
        Layer 8: Contract testing - time series output validation.
        """
        connector.connect()
        connector.load_presidential_data(sample_presidential_data)
        
        result = connector.get_state_trends(state='PA')
        
        assert isinstance(result, pd.DataFrame), "Should return DataFrame"
        
        # Verify expected columns
        expected_columns = [
            'year', 'dem_votes', 'rep_votes', 'total_votes',
            'dem_share', 'rep_share', 'margin'
        ]
        for col in expected_columns:
            assert col in result.columns, f"Missing expected column: {col}"
        
        # Verify multiple years
        assert len(result) == 2, "Should have 2 years of data (2016, 2020)"
        assert 2016 in result['year'].values, "Should include 2016"
        assert 2020 in result['year'].values, "Should include 2020"
        
        # Verify sorted by year
        years = result['year'].tolist()
        assert years == sorted(years), "Should be sorted by year"
