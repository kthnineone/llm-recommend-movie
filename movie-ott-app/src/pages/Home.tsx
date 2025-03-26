// pages/Home.tsx  
import React, { useState, useEffect } from "react";
import SearchBar from "../components/SearchBar";
import MovieCard from "../components/MovieCard";
import UserSearchBar from "../components/UserSearchBar";
import { useNavigate } from 'react-router-dom';
import styles from './Home.module.css'

const API_URL = import.meta.env.VITE_API_URL;


interface Movie {
    movieId: number;
    title: string;
    rating: number;
    genre: string;
}

// 인기 영화 목록 (고정)
const popularMovies: Movie[] = [
    {movieId: 1, title: "The Matrix", rating: 4.8, genre: "Action"},
    {movieId: 2, title: "Inception", rating: 4.7, genre: "Sci-Fi"},
    {movieId: 3, title: "Godfather", rating: 4.6, genre: "Crime"},
];

// 추천 영화 목록 (고정)
const recommendedMovies: Movie[] = [
    {movieId: 1, title: "The Matrix", rating: 4.8, genre: "Action"},
    {movieId: 2, title: "Inception", rating: 4.7, genre: "Sci-Fi"},
    {movieId: 3, title: "Godfather", rating: 4.6, genre: "Crime"},
];



const Home: React.FC = () => {
    const [search, setSearch] = useState<string>("");
    const [userId, setUserId] = useState<number | null>(null);
    const [createUserId, setCreateUserId] = useState<number | null>(null);
    const [getUserId, setGetUserId] = useState<number | null>(null);
    const [userRecommendedMovies, setUserRecommendedMovies] = useState<Movie[]>([]);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchRecommendedMovies = async () => {
            const userId = 1;
            try {
                const response = await fetch(`${API_URL}/api/recommended?userId=${encodeURIComponent(userId)}`);
                if (!response.ok) {
                    throw new Error(`추천 영화 불러오기 실패: ${response.status}`);
                }
                const recommendations = await response.json();
                setUserRecommendedMovies(recommendations);
            } catch (error) {
                console.error('Error:', error);
                alert('추천 영화 불러오기 중 오류가 발생했습니다: ' + error);
            }
        };

        fetchRecommendedMovies();
    }, []); // Empty dependency array means this effect runs once when the component mounts


    const handleSearch = async () => {
        if (!search.trim()) {
            alert('검색어를 입력해주세요');
            return;
        }
        console.log(API_URL);

        try {
            const response = await fetch(`${API_URL}/api/search?query=${encodeURIComponent(search)}`);
            if (!response.ok) {
                throw new Error(`검색 실패: ${response.status}`);
            }
            const searchResults = await response.json();
            
            navigate('/search-results', {
                state: {
                    results: searchResults,
                    query: search
                }
            });
        } catch (error) {
            console.error('Error:', error);
            alert('검색 중 오류가 발생했습니다: ' + error);
        }
    };

    const handleUserCreateRecommendSearch = async () => {
        if (!createUserId) {
            alert('유저 ID를 입력해주세요');
            return;
        }

        try {
            {/* 추천 영화 등록, POST part*/}
            const json_body = {userId: createUserId};
            console.log(json_body);
            const response = await fetch(`${API_URL}/api/recommend`, {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify(json_body)
              });
            
            if (!response.ok) {
                throw new Error(`추천 영화 등록 실패: ${response.status}`);
            };
        }
        catch (error) {
            console.error('Error:', error);
            alert('추천 영화를 등록하는 중 오류가 발생했습니다: ' + error);
        }
    };

    const handleUserGetRecommendSearch = async () => {
        if (!getUserId) {
            alert('유저 ID를 입력해주세요');
            return;
        }

        try {
            {/* 추천 영화 불러오기, GET part*/}
            const json_body = {userId: getUserId};
            console.log(json_body);
            const response = await fetch(`${API_URL}/api/recommended?userId=${encodeURIComponent(getUserId)}`);
            if (!response.ok) {
                throw new Error(`추천 영화 불러오기 실패: ${response.status}`);
            }
            const Recommendations = await response.json();
            
            navigate(`/user/${getUserId}`, {
                state: {
                    results: Recommendations,
                    query: getUserId
                }
            });
        } catch (error) {
            console.error('Error:', error);
            alert('추천 영화 불러오기 중 오류가 발생했습니다: ' + error);
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            {/* 검색 섹션 */}
            <div className="mb-12">
                <h1 className="text-3xl font-bold text-center mb-8">영화 검색</h1>
                <div className={styles.searchContainer}>
                    <div>
                    <SearchBar 
                        search={search} 
                        setSearch={setSearch} 
                        onSearch={handleSearch}
                    />
                    </div>
                    <div>
                    <button 
                        onClick={handleSearch}
                        className={styles.searchButton}
                    >
                        검색
                    </button>
                    </div>
                </div>
            </div>

            {/* 인기 영화 섹션 */}
            <div className="mt-8">
                {/* text-2xl이란 1.5rem 24px */}
                <h2 className="text-3xl font-bold mb-6">인기 영화</h2>
                {/* 그리드 방식 <div className="grid grid-cols-1 md:grid-cols-3 gap-6"> */}
                {/*recommendedMovies.map((movie) => (
                        <MovieCard key={movie.movieId} movie={movie} />
                    ))*/}
                <div className={styles.popularContainer}>
                    {popularMovies.map((movie) => (
                        <div key={movie.movieId} className="flex-shrink-0">
                            <MovieCard movie={movie} />
                        </div>
                    ))} 
                </div>
            </div>

            {/* 추천 영화 섹션 */}
            <div className="mt-8">
                {/* text-2xl이란 1.5rem 24px */}
                <h2 className="text-3xl font-bold mb-6">추천 영화</h2>
                {/* 그리드 방식 <div className="grid grid-cols-1 md:grid-cols-3 gap-6"> */}
                {/*recommendedMovies.map((movie) => (
                        <MovieCard key={movie.movieId} movie={movie} />
                    ))*/}
                <div className={styles.recommendContainer}>
                    {/* 5개만 보여주는 경우 */}
                    {userRecommendedMovies.slice(0, 5).map((movie) => (
                        <div key={movie.movieId} className="flex-shrink-0">
                            <MovieCard movie={movie} />
                        </div>
                    ))} 
                </div>
            </div>

             {/* 추천 영화 생성 확인 섹션 */}
             <div className="mt-8">
                <h2 className="text-3xl font-bold mb-6">유저 기반 추천 영화 등록</h2>
                <div className={styles.searchContainer}>
                    <div>
                    <UserSearchBar 
                        search={createUserId} 
                        setSearch={setCreateUserId} 
                        onSearch={handleUserCreateRecommendSearch}
                    />
                    </div>
                    <div>
                    <button 
                        onClick={handleUserCreateRecommendSearch}
                        className={styles.searchButton}
                    >
                        생성
                    </button>
                    </div>
                </div>
            </div>

            {/* 추천 영화 불러오기 확인 섹션 */}
            <div className="mt-8">
                <h2 className="text-3xl font-bold mb-6">유저 기반 추천 영화 불러오기</h2>
                <div className={styles.searchContainer}>
                    <div>
                    <UserSearchBar 
                        search={getUserId} 
                        setSearch={setGetUserId} 
                        onSearch={handleUserGetRecommendSearch}
                    />
                    </div>
                    <div>
                    <button 
                        onClick={handleUserGetRecommendSearch}
                        className={styles.searchButton}
                    >
                        불러오기
                    </button>
                    </div>
                </div>
            </div>

        </div>
    );
};

export default Home;
