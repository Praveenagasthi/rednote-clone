import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function EditProfile() {
  const [displayName, setDisplayName] = useState("");
  const [bio, setBio] = useState("");
  const [avatar, setAvatar] = useState(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    const loadProfile = async () => {
      const token = localStorage.getItem("access_token");

      if (!token) {
        setError("You must be logged in.");
        setLoading(false);
        return;
      }

      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        const userId = payload.user_id;

        const response = await api.get(
          `auth/users/${userId}/`
        );

        setDisplayName(response.data.display_name || "");
        setBio(response.data.bio || "");
      } catch (err) {
        console.error(err);
        setError("Failed to load profile.");
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setSaving(true);
    setError("");

    try {
      const formData = new FormData();

      formData.append("display_name", displayName);
      formData.append("bio", bio);

      if (avatar) {
        formData.append("avatar", avatar);
      }

      await api.patch(
        "auth/users/me/update/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      navigate("/profile");
    } catch (err) {
      console.error(err);

      if (err.response?.data) {
        setError(JSON.stringify(err.response.data));
      } else {
        setError("Failed to update profile.");
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <p>Loading profile...</p>;
  }

  if (error && !displayName && !bio) {
    return <p>{error}</p>;
  }

  return (
    <main className="edit-profile-page">
      <div className="edit-profile-container">

        <div className="edit-profile-header">
          <button
            type="button"
            className="edit-profile-back-button"
            onClick={() => navigate("/profile")}
          >
            ←
          </button>

          <h1>Edit Profile</h1>

          <div className="edit-profile-header-spacer"></div>
        </div>

        <form
          className="edit-profile-form"
          onSubmit={handleSubmit}
        >
          <div className="edit-profile-field">
            <label htmlFor="display-name">
              Display Name
            </label>

            <input
              id="display-name"
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
            />
          </div>

          <div className="edit-profile-field">
            <label htmlFor="bio">
              Bio
            </label>

            <textarea
              id="bio"
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              rows="5"
            />
          </div>

          <div className="edit-profile-field">
            <label htmlFor="avatar">
              Avatar
            </label>

            <input
              id="avatar"
              className="edit-profile-file-input"
              type="file"
              accept="image/*"
              onChange={(e) => setAvatar(e.target.files[0])}
            />

            {avatar && (
              <p className="edit-profile-file-name">
                {avatar.name}
              </p>
            )}
          </div>

          {error && (
            <div className="edit-profile-error">
              {error}
            </div>
          )}

          <div className="edit-profile-actions">
            <button
              type="button"
              className="edit-profile-cancel-button"
              onClick={() => navigate("/profile")}
              disabled={saving}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="edit-profile-save-button"
              disabled={saving}
            >
              {saving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </form>

      </div>
    </main>
  );
}

export default EditProfile;