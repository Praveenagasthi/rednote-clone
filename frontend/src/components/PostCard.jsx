import { Link } from "react-router-dom";
import { useState } from "react";
import api from "../services/api";
import Comments from "./Comments";

function PostCard({ post, onPostUpdate }) {
    
  const [commentCount, setCommentCount] = useState(
      post.comment_count || 0
    );

  const handleLike = async () => {
    try {
      const response = await api.post(`posts/${post.id}/like/`);

      onPostUpdate?.({
        id: post.id,
        likes_count: response.data.likes_count,
        liked_by_me: response.data.liked,
      });
    } catch (error) {
      console.error(error);
    }
  };

  const handleSave = async () => {
    try {
      const response = await api.post(`posts/${post.id}/save/`);

      onPostUpdate?.({
        id: post.id,
        saves_count: response.data.saves_count,
        saved_by_me: response.data.saved,
      });
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <article className="post-card">
      <div className="post-header">
        <Link
          className="post-author"
          to={`/users/${post.author_id}`}
        >
          {post.author}
        </Link>

        {post.location && (
          <span className="post-location">
            · {post.location}
          </span>
        )}
      </div>

      <Link
        className="post-content"
        to={`/posts/${post.id}`}
      >
        <div
          className={`post-images ${
            post.images?.length > 1 ? "multiple" : "single"
          }`}
        >
          {post.images?.map((image) => (
            <img
              className="post-image"
              key={image.id}
              src={image.image}
              alt=""
            />
          ))}
        </div>

        {post.caption && (
          <p className="post-caption">
            {post.caption}
          </p>
        )}
      </Link>

      <div className="post-actions">
        <button onClick={handleLike}>
          {post.liked_by_me ? "❤️ Liked" : "♡ Like"} (
          {post.likes_count || 0})
        </button>

        <button onClick={handleSave}>
          🔖 {post.saved_by_me ? "Saved" : "Save"} (
          {post.saves_count || 0})
        </button>

        <span className="comment-count">
          💬 {commentCount}
        </span>
      </div>

      <div className="post-comments">
        <Comments postId={post.id} onCommentCountChange={setCommentCount} />
      </div>
    </article>
  );
}

export default PostCard;