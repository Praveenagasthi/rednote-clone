import { useEffect, useState } from "react";
import api from "../services/api";
import PostCard from "../components/PostCard";

function Saved() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadSavedPosts = async () => {
      try {
        const response = await api.get("posts/saved/");

        setPosts(response.data.results || response.data || []);
      } catch (err) {
        console.error(err);
        setError("Failed to load saved posts.");
      } finally {
        setLoading(false);
      }
    };

    loadSavedPosts();
  }, []);

  const handlePostUpdate = (updatedPost) => {
    setPosts((currentPosts) =>
      updatedPost.saved_by_me === false
        ? currentPosts.filter((post) => post.id !== updatedPost.id)
        : currentPosts.map((post) =>
            post.id === updatedPost.id
              ? { ...post, ...updatedPost }
              : post
          )
    );
  };

  if (loading) {
    return <p>Loading saved posts...</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }

  return (
    <main className="saved-page">
      <div className="saved-container">

        <div className="saved-header">
          <h1>Saved Posts</h1>
          <p>Your saved posts</p>
        </div>

        {posts.length === 0 ? (
          <div className="saved-empty">
            <div className="saved-empty-icon">🔖</div>
            <h2>No saved posts yet</h2>
            <p>
              Posts you save will appear here.
            </p>
          </div>
        ) : (
          <div className="saved-posts">
            {posts.map((post) => (
              <PostCard
                key={post.id}
                post={post}
                onPostUpdate={handlePostUpdate}
              />
            ))}
          </div>
        )}

      </div>
    </main>
  );
}

export default Saved;