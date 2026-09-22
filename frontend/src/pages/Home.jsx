import { useEffect, useState } from "react";
import api from "../services/api";
import PostCard from "../components/PostCard";

function Home() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadFeed = async () => {
      try {
        const response = await api.get("feed/");
        setPosts(response.data.results || []);
      } catch (err) {
        console.error(err);
        setError("Failed to load feed.");
      } finally {
        setLoading(false);
      }
    };

    loadFeed();
  }, []);

  if (loading) {
    return <p>Loading feed...</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }

  return (
    <main className="home-page">
      <h1 className="home-title">Home Feed</h1>

      {posts.length === 0 ? (
        <p>No posts yet.</p>
      ) : (
        posts.map((post) => (
          <PostCard
              key={post.id}
              post={post}
              onPostUpdate={(updatedPost) => {
                setPosts((currentPosts) =>
                  currentPosts.map((currentPost) =>
                    currentPost.id === updatedPost.id
                      ? { ...currentPost, ...updatedPost }
                      : currentPost
                  )
                );
              }}
            />
        ))
      )}
    </main>
  );
}

export default Home;