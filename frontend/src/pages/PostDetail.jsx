import { useEffect, useState } from "react";
import { Link,useNavigate,useParams } from "react-router-dom";
import api from "../services/api";
import Comments from "../components/Comments";

function PostDetail() {
    const { postId } = useParams();
    const navigate = useNavigate();
    const [post, setPost] = useState(null);
    const [liked, setLiked] = useState(false);
    const [saved, setSaved] = useState(false);
    const [likeCount, setLikeCount] = useState(0);
    const [saveCount, setSaveCount] = useState(0);
    const [commentCount, setCommentCount] = useState(0);
    const [editing, setEditing] = useState(false);
    const [editCaption, setEditCaption] = useState("");
    const [editLocation, setEditLocation] = useState("");
    const [actionLoading, setActionLoading] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

  useEffect(() => {
    const loadPost = async () => {
      try {
        const response = await api.get(`posts/${postId}/`);
        setPost(response.data);
        setLiked(response.data.liked_by_me);
        setSaved(response.data.saved_by_me);
        setLikeCount(response.data.likes_count || 0);
        setSaveCount(response.data.saves_count || 0);
        setCommentCount(response.data.comment_count || 0);
      } catch (err) {
        console.error(err);
        setError("Failed to load post.");
      } finally {
        setLoading(false);
      }
    };

    loadPost();
  }, [postId]);

  const handleLike = async () => {
    try {
        const response = await api.post(
        `posts/${post.id}/like/`
        );

        setLiked(response.data.liked);
        setLikeCount(response.data.likes_count);
    } catch (err) {
        console.error(err);
    }
    };

  const handleSave = async () => {
    try {
        const response = await api.post(
        `posts/${post.id}/save/`
        );

        setSaved(response.data.saved);
        setSaveCount(response.data.saves_count);
    } catch (err) {
        console.error(err);
    }
    };

    const handleEdit = () => {
      setEditCaption(post.caption || "");
      setEditLocation(post.location || "");
      setEditing(true);
    };

    const handleCancelEdit = () => {
      setEditing(false);
    };

    const handleUpdate = async (e) => {
      e.preventDefault();

      setActionLoading(true);

      try {
        const response = await api.patch(
          `posts/${post.id}/`,
          {
            caption: editCaption,
            location: editLocation,
          }
        );

        setPost(response.data);
        setEditing(false);
      } catch (err) {
        console.error(err);
      } finally {
        setActionLoading(false);
      }
    };

    const handleDelete = async () => {
      const confirmed = window.confirm(
        "Are you sure you want to delete this post?"
      );

      if (!confirmed) {
        return;
      }

      setActionLoading(true);

      try {
        await api.delete(`posts/${post.id}/`);
        navigate("/");
      } catch (err) {
        console.error(err);
        setActionLoading(false);
      }
    };

  if (loading) {
    return <p>Loading post...</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }

  if (!post) {
    return <p>Post not found.</p>;
  }

  return (
    <main className="post-detail-page">
      <div className="post-detail-container">
        <div className="post-detail-header">
          <Link
            className="post-detail-author"
            to={`/users/${post.author_id}`}
          >
            {post.author}
          </Link>

          {post.location && (
            <span className="post-detail-location">
              · {post.location}
            </span>
          )}

          {post.is_owner && !editing && (
            <div className="post-owner-actions">
              <button
                className="post-edit-button"
                onClick={handleEdit}
              >
                Edit
              </button>

              <button
                className="post-delete-button"
                onClick={handleDelete}
                disabled={actionLoading}
              >
                Delete
              </button>
            </div>
          )}
        </div>

        {editing ? (
          <form
            className="post-edit-form"
            onSubmit={handleUpdate}
          >
            <div className="post-edit-field">
              <label htmlFor="edit-caption">Caption</label>

              <textarea
                id="edit-caption"
                value={editCaption}
                onChange={(e) => setEditCaption(e.target.value)}
                maxLength={2000}
              />
            </div>

            <div className="post-edit-field">
              <label htmlFor="edit-location">Location</label>

              <input
                id="edit-location"
                type="text"
                value={editLocation}
                onChange={(e) => setEditLocation(e.target.value)}
                maxLength={255}
              />
            </div>

            <div className="post-edit-actions">
              <button
                type="submit"
                className="post-save-changes-button"
                disabled={actionLoading}
              >
                {actionLoading ? "Saving..." : "Save Changes"}
              </button>

              <button
                type="button"
                className="post-cancel-button"
                onClick={handleCancelEdit}
                disabled={actionLoading}
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          post.caption && (
            <p className="post-detail-caption">
              {post.caption}
            </p>
          )
        )}

        <div className="post-detail-images">
          {post.images?.map((image) => (
            <img
              className="post-detail-image"
              key={image.id}
              src={image.image}
              alt=""
            />
          ))}
        </div>

        <div className="post-detail-actions">
          <button onClick={handleLike}>
            {liked ? "❤️ Liked" : "♡ Like"} ({likeCount})
          </button>

          <button onClick={handleSave}>
            {saved ? "🔖 Saved" : "🔖 Save"} ({saveCount})
          </button>

          <span className="post-detail-comment-count">
            💬 {commentCount}
          </span>
        </div>

        <div className="post-detail-comments">
          <Comments postId={post.id} onCommentCountChange={setCommentCount} />
        </div>
      </div>
    </main>
  );
}

export default PostDetail;