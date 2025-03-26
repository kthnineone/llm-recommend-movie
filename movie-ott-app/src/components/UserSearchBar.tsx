import React, { useState } from 'react';
import styles from './Searchbar.module.css'

interface SearchBarProps {
    search: string;
    setSearch: (search: string) => void;
    onSearch?: () => void;
}

const UserSearchBar: React.FC<SearchBarProps> = ({ search, setSearch, onSearch }) => {
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
                placeholder="유저 ID로 검색하세요."
                className={styles.searchInput}
            />
        </div>
    );
};

export default UserSearchBar;

