import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import SearchBar from './components/SearchBar';
import MovieList from './components/MovieList';
import SearchResults from './pages/SearchResults';
import UserRecommendations from './pages/UserRecommendations';
import Home from './pages/Home';
import './App.css'

/* 
React Router를 사용
<div> 아래, <Routes> 위에 있던 
<SearchBar /> 를 삭제해본다  
*/
const App: React.FC = () => {
  return (
    <Router>
      <div className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search-results" element={<SearchResults />} />
          <Route path="/user/:userId" element={<UserRecommendations />} /> {/* 새로운 라우트 추가 */}
        </Routes>
      </div>
    </Router>
  );
};

export default App;

