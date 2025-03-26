import React, { useState } from 'react';
import styles from './Searchbar.module.css'

interface SearchBarProps {
    search: string;
    setSearch: (search: string) => void;
    onSearch?: () => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ search, setSearch, onSearch }) => {
    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && onSearch) {
            onSearch();
        }
    };

    return (
        <div className={styles.searchContainer}>
            <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="제목이나 장르로 영화를 검색하세요."
                className={styles.searchInput}
            />
        </div>
    );
};

export default SearchBar;

