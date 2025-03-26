import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
// 같은 폴더에 있는 경우 ./tsxfile.tsx로 import 가능
import MovieCard from '../components/MovieCard';

interface Movie {
    id: number;
    title: string;
    rating: number;
    genre: string;
}

const SearchResults: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const searchResults = location.state?.results as Movie[];
    const searchQuery = location.state?.query as string;

    const handleBackToHome = () => {
        navigate('/');
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex items-center justify-between mb-8">
                <h1 className="text-2xl font-bold">"{searchQuery}" 검색 결과</h1>
                <button 
                    onClick={handleBackToHome}
                    className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                >
                    홈으로 돌아가기
                </button>
            </div>

            {searchResults?.length === 0 ? (
                <div className="text-center py-12">
                    <p className="text-gray-500 text-lg">검색 결과가 없습니다.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {searchResults?.map((movie) => (
                        <MovieCard key={movie.id} movie={movie} />
                    ))}
                </div>
            )}
        </div>
    );
};

export default SearchResults;