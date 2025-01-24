import Head from "next/head";
import { useState, useEffect, useRef } from "react";
import styles from "./index.module.css";

export default function Home() {
  const [query, setQuery] = useState("");
  const [images, setImages] = useState([]);
  const [displayQuery, setDisplayQuery] = useState("");
  const imageContainerRef = useRef(null);

  const searchQuery = async (query) => {
      const response = await fetch("/api/search/?query=" + query);
      const data = await response.json();
      setImages(data);
      setDisplayQuery(`Showing results for "${query}"`);
  };

  const onSubmit = (event) => {
    event.preventDefault();
    if (!query.trim()) return;
    searchQuery(query.trim());
    setQuery("");
  };

  return (
    <div>
      <Head>
        <title>Image search</title>
      </Head>
      <h1 className={styles.heading1}>Vespa Image Search template</h1>
      <div className={styles.searchInputContainer}>
        <form className={styles.form} onSubmit={onSubmit}>
          <input
            className={styles.textarea}
            name="message"
            placeholder="A child playing football"
            required
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          ></input>
            <input className={styles.inputSubmit} type="submit" value="Search" />
        </form>
      </div>
      {
          (displayQuery.trim().length > 0 ? <p className={styles.text}>{displayQuery.trim()}</p> : "")
      }
      <div className={styles.imageContainer} ref={imageContainerRef}>
        {images.map((image_obj, index) => (
            <div className={styles.imageCard}>
                <img key={index} src={"/api/img/" + image_obj.filename} className={styles.image} />
                <div className={styles.overlay}>
                    <p className={styles.overlayText}>{`Relevance: ${image_obj.relevance.toFixed(4)}`}</p>
                </div>
            </div>
        ))}
      </div>
    </div>
  );
}

