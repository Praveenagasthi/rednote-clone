import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function CreatePost() {
  const [caption, setCaption] = useState("");
  const [location, setLocation] = useState("");
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleImageChange = (e) => {
    const selectedImages = Array.from(e.target.files);
    setImages(selectedImages);
  };

  const handleRemoveImage = (indexToRemove) => {
    setImages((currentImages) =>
      currentImages.filter((_, index) => index !== indexToRemove)
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (loading) {
      return;
    }

    setError("");

    if (images.length === 0) {
      setError("Please select at least one image.");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();

      formData.append("caption", caption);
      formData.append("location", location);

      images.forEach((image) => {
        formData.append("images", image);
      });

      await api.post("posts/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      navigate("/");
    } catch (err) {
      console.error(err);

      if (err.response?.data) {
        const data = err.response.data;

        if (typeof data === "string") {
          setError(data);
        } else if (data.detail) {
          setError(data.detail);
        } else if (data.images) {
          setError(
            Array.isArray(data.images)
              ? data.images.join(" ")
              : data.images
          );
        } else if (data.caption) {
          setError(
            Array.isArray(data.caption)
              ? data.caption.join(" ")
              : data.caption
          );
        } else if (data.location) {
          setError(
            Array.isArray(data.location)
              ? data.location.join(" ")
              : data.location
          );
        } else {
          setError("Unable to create post. Please check your information.");
        }
      } else {
        setError("Unable to connect to the server.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-post-page">
      <div className="create-post-container">
        <div className="create-post-header">
          <button
            type="button"
            className="back-button"
            onClick={() => navigate(-1)}
          >
            ←
          </button>

          <h1>Create Post</h1>

          <div className="create-post-header-spacer"></div>
        </div>

        <form onSubmit={handleSubmit} className="create-post-form">
          <div className="create-post-section">
            <label className="create-post-label">Photos</label>

            <label className="image-upload-box">
              <span className="upload-icon">＋</span>
              <span>Add Photos</span>

              <input
                type="file"
                accept="image/*"
                multiple
                onChange={handleImageChange}
              />
            </label>

            {images.length > 0 && (
              <div className="image-count">
                {images.length} image{images.length !== 1 ? "s" : ""} selected
              </div>
            )}

            {images.length > 0 && (
              <div className="image-preview-grid">
                {images.map((image, index) => (
                  <div className="image-preview" key={index}>
                    <img
                      src={URL.createObjectURL(image)}
                      alt={`Preview ${index + 1}`}
                    />

                    <button
                      type="button"
                      className="remove-image-button"
                      onClick={() => handleRemoveImage(index)}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="create-post-section">
            <label className="create-post-label" htmlFor="caption">
              Caption
            </label>

            <textarea
              id="caption"
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              maxLength={2000}
              placeholder="Share your thoughts..."
              rows="5"
            />

            <div className="character-count">
              {caption.length}/2000
            </div>
          </div>

          <div className="create-post-section">
            <label className="create-post-label" htmlFor="location">
              Location
            </label>

            <input
              id="location"
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              maxLength={255}
              placeholder="Add a location"
            />
          </div>

          {error && <div className="create-post-error">{error}</div>}

          <button
            type="submit"
            className="create-post-button"
            disabled={loading}
          >
            {loading ? "Creating..." : "Publish"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default CreatePost;