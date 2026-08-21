import React, { use } from "react";
import { useEffect, useState } from "react";
import axios from "axios";
import CardContainer from "../MovieCard/MovieCard";

const Section = () => {
  const [movies, setMovies] = useState([]);

  useEffect(() => {
    axios
      .get("https://zhamal-tv.netlify.app/cartoons/get_all")
      .then((data) => setMovies(data.data));
  }, []);

  return (
    <div className="section-container">
      {movies.map((movie) => (
        <CardContainer key={movie.id} movie={movie} />
      ))}
    </div>
  );
};

export default Section;