import { useEffect, useState } from "react";
import api from "../services/api";

function getUserIdFromToken() {
  const token = localStorage.getItem("access_token");

  if (!token) return null;

  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.user_id;
  } catch (error) {
    console.error("Failed to read access token:", error);
    return null;
  }
}

function Comments({ postId, onCommentCountChange }) {
  const currentUserId = getUserIdFromToken();
  const [comments, setComments] = useState([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    const fetchComments = async () => {
      try {
        const response = await api.get(`posts/${postId}/comments/`);

        if (!cancelled) {
          setComments(response.data.results || response.data);
        }
      } catch (err) {
        console.error(err);

        if (!cancelled) {
          setError("Failed to load comments.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchComments();

    return () => {
      cancelled = true;
    };
  }, [postId]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!text.trim()) {
      return;
    }

    setSubmitting(true);
    setError("");

    try {
      await api.post(`posts/${postId}/comments/`, {
        text: text.trim(),
      });

      setText("");

      const response = await api.get(`posts/${postId}/comments/`);
      setComments(response.data.results || response.data);

      onCommentCountChange?.((currentCount) => currentCount + 1);
    } catch (err) {
      console.error(err);
      setError("Failed to add comment.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (commentId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this comment?"
    );

    if (!confirmed) {
      return;
    }

    try {
      await api.delete(`posts/comments/${commentId}/delete/`);

      setComments((currentComments) =>
        currentComments.filter((comment) => comment.id !== commentId)
      );

      onCommentCountChange?.((currentCount) =>
        Math.max(0, currentCount - 1)
      );
    } catch (err) {
      console.error(err);
      setError("Failed to delete comment.");
    }
  };

  return (
    <div className="comments-section">
      <h3>Comments</h3>

      {loading && (
        <p className="comments-status">Loading comments...</p>
      )}

      {error && <p className="comments-error">{error}</p>}

      {!loading && comments.length === 0 && (
        <p className="comments-status">No comments yet.</p>
      )}

      <div className="comments-list">
        {comments.map((comment) => (
          <div className="comment" key={comment.id}>
            <strong className="comment-user">
              {comment.user}
            </strong>

            <p className="comment-text">
              {comment.text}
            </p>

            {Number(comment.user_id) === Number(currentUserId) && (
              <button
                className="comment-delete"
                onClick={() => handleDelete(comment.id)}
              >
                Delete
              </button>
            )}
          </div>
        ))}
      </div>

      <form className="comment-form" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Write a comment..."
          value={text}
          onChange={(e) => setText(e.target.value)}
        />

        <button type="submit" disabled={submitting}>
          {submitting ? "Posting..." : "Comment"}
        </button>
      </form>
    </div>
  );
}

export default Comments;