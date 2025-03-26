import React, { useState } from 'react';


const API_URL = import.meta.env.VITE_API_URL;

interface MovieItemProps {
    title: string;
    movieId: number;
    userId: number;
}

const MovieItem: React.FC<MovieItemProps> = ({ title, movieId, userId }) => {
    const [rating, setRating] = useState<number | null>(null);
  
    const handleRating = async () => {
      if (rating !== null) {
        await fetch(`${API_URL}/api/ratings`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ userId, movieId, rating }),
        });
        alert('Rating added successfully');
      }
    };
  
    return (
      <div>
        <h3>{title}</h3>
        <input
          type="number"
          min="1"
          max="5"
          value={rating ?? ''}
          onChange={(e) => setRating(Number(e.target.value))}
          placeholder="Rate this movie"
        />
        <button onClick={handleRating}>Submit Rating</button>
      </div>
    );
  };

export default MovieItem;
