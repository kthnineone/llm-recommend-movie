import React from 'react';
import styles from './MovieItem.module.css';

interface MovieListProps{
    movies: {
        movieId: number;
        title: string;
        genre: string;
        poster: string;
     }[];
}

/*
이미지 포함 버젼
<div className={styles.movieGrid}>
          {movies.map(movie => (
            <div key={movie.movieId} className={styles.movieCard}>
              <img src={movie.poster} alt={movie.title} />
              <h3>{movie.title}</h3>
            </div>
          ))}
        </div>
*/

const MovieList: React.FC<MovieListProps> = ({ movies }) => {
  
    return (
      <div className={styles.movieListContainer}>
        <h2 className={styles.title}>추천 영화</h2>
        <div className={styles.movieGrid}>
          {movies.map(movie => (
            <div key={movie.movieId} className={styles.movieCard}>
              <h3>{movie.title}</h3>
            </div>
          ))}
        </div>
      </div>
    );
  };

export default MovieList;
