// MovieCards  
import React, { useState } from 'react';
import styles from './MovieCard.module.css'

const API_URL = import.meta.env.VITE_API_URL;

interface Movie {
    movieId: number;
    title: string;
    rating: number;
    genre: string;
}


interface MovieCardProps {
    movie: Movie;
    userId: number;
}


const MovieCard: React.FC<MovieCardProps> = ({ movie, userId = 230213 }) => {
    const [showRating, setShowRating] = useState(false);
    const [userRating, setUserRating] = useState<number | null>(null);

    /* Mouse and corresponding rating card Control */
    const handleMouseEnter = () => {
        setShowRating(true);
    };

    const handleMouseLeave = () => {
        setShowRating(false);
    };

    const handleRatingChange = (rating: number) => {
        setUserRating(rating);
      };

    const handleRatingSubmit = async () => {
        if (userRating !== null) {
            try {

              const timestamp = new Date();
              const isoTimestampString = timestamp.toISOString();
              
              console.log(timestamp);
              console.log(isoTimestampString);
              console.log(userId);
              console.log(movie.movieId);
              console.log(userRating);

              const jsonBody = {
                userId: userId,
                movieId: movie.movieId,
                rating: userRating,
                timestamp: isoTimestampString,
              };

              const response = await fetch(`${API_URL}/api/ratings`, {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify(jsonBody)
                /*body: JSON.stringify({ userId: userId, 
                                        movieId: movie.movieId, 
                                        rating: userRating }),*/
              });
      
              if (response.ok) {
                alert('Rating added successfully');
                setShowRating(false); // 제출 후 별점 창 숨김
              } else {
                alert('Failed to add rating');
              }
            } catch (error) {
              console.error('Error submitting rating:', error);
              alert('An error occurred while submitting rating');
            }
          }
      };


    return (
        <div
          className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow relative"
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
         >
            <div className="p-6">
                <h3 className="text-xl font-semibold mb-2">{movie.title}</h3>
                <div className="flex flex-col">
                    <span>평점: {movie.rating}</span>
                    <span>장르: {movie.genre}</span>
                </div>
            </div>
            {showRating && (
                <div className="absolute top-0 left-0 w-full h-full bg-black bg-opacity-50 flex items-center justify-center">
                    <div className="bg-white p-6 rounded-log">
                        <h4 className="text-lg font-semibold mb-4">별점 매기기</h4>
                        <div className="flex items-center space-x-2">
                        {[1, 2, 3, 4, 5].map((rating) => (
                            <button
                                key={rating}
                                className={`text-2xl ${userRating && userRating >= rating ? 'text-yellow-500' : 'text-gray-300'}`}
                                onClick={() => handleRatingChange(rating)}
                            >
                            ★
                            </button>
                        ))}
                    </div>
                    {userRating && <p className="mt-4">선택한 별점: {userRating}</p>}
                    <button className="mt-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onClick={handleRatingSubmit}>
                    Submit Rating
                    </button>
                </div>
            </div>
            )}
        </div>
    );
};

export default MovieCard;

