import { useEffect, useState } from "react";
import { Link, useParams  } from "react-router-dom";
import api from "../services/api";
import PostCard from "../components/PostCard";

function getUserIdFromToken() {
  const token = localStorage.getItem("access_token");

  if (!token) {
    return null;
  }

  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.user_id;
  } catch (error) {
    console.error("Failed to read access token:", error);
    return null;
  }
}

function Profile() {
  const { userId } = useParams();
  const [profile, setProfile] = useState(null);
  const [isFollowing, setIsFollowing] = useState(false);
  const [followLoading, setFollowLoading] = useState(false);
  const [posts, setPosts] = useState([]);
  const [followers, setFollowers] = useState([]);
  const [showFollowers, setShowFollowers] = useState(false);
  const [following, setFollowing] = useState([]);
  const [showFollowing, setShowFollowing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadProfile = async () => {
    const viewedUserId = userId || getUserIdFromToken();

    if (!viewedUserId) {
      setError("You must be logged in.");
      setLoading(false);
      return;
    }

      try {
        const [profileResponse, postsResponse] = await Promise.all([
          api.get(`auth/users/${viewedUserId}/`),
          api.get(`auth/users/${viewedUserId}/posts/`),
        ]);

        setProfile(profileResponse.data);
        setIsFollowing(profileResponse.data.is_following);
        setPosts(postsResponse.data.results || []);
      } catch (err) {
        console.error(err);
        setError("Failed to load profile.");
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, [userId]);

  

  if (loading) {
    return <p>Loading profile...</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }


  const handleFollowers = async () => {
    if (showFollowers) {
      setShowFollowers(false);
      return;
    }

    const viewedUserId = userId || getUserIdFromToken();

    if (!viewedUserId) {
      return;
    }

    try {
      const response = await api.get(
        `auth/users/${viewedUserId}/followers/`
      );

      setFollowers(response.data.results || response.data);
      setShowFollowers(true);
    } catch (err) {
      console.error(err);
    }
  };

  const handleFollowing = async () => {
    if (showFollowing) {
      setShowFollowing(false);
      return;
    }

    const viewedUserId = userId || getUserIdFromToken();

    if (!viewedUserId) {
      return;
    }

    try {
      const response = await api.get(
        `auth/users/${viewedUserId}/following/`
      );

      setFollowing(response.data.results || response.data);
      setShowFollowing(true);
    } catch (err) {
      console.error(err);
    }
  };

  const handleFollowToggle = async () => {
    if (!profile || followLoading) {
      return;
    }

    setFollowLoading(true);

    try {
      const response = await api.post(
        `auth/users/${profile.id}/follow/`
      );

      setIsFollowing(response.data.following);

      setProfile((currentProfile) => ({
        ...currentProfile,
        followers_count:
          currentProfile.followers_count +
          (response.data.following ? 1 : -1),
      }));

      // Refresh followers list if it is currently being shown
      if (showFollowers) {
        const followersResponse = await api.get(
          `auth/users/${profile.id}/followers/`
        );

        setFollowers(
          followersResponse.data.results || followersResponse.data
        );
      }
    } catch (err) {
      console.error(err);
    } finally {
      setFollowLoading(false);
    }
  };

  return (
    <main className="profile-page">
      <div className="profile-container">

        <div className="profile-header">
          <div className="profile-avatar">
            {profile.avatar ? (
              <img
                src={profile.avatar}
                alt="Profile"
              />
            ) : (
              <div className="profile-avatar-placeholder">
                {profile.username?.charAt(0).toUpperCase()}
              </div>
            )}
          </div>

          <div className="profile-info">
            <div className="profile-top-row">
              <h1 className="profile-username">
                {profile.username}
              </h1>

              {Number(profile.id) === Number(getUserIdFromToken()) && (
                <Link
                  to="/profile/edit"
                  className="profile-edit-button"
                >
                  Edit Profile
                </Link>
              )}

              {Number(profile.id) !== Number(getUserIdFromToken()) && (
                <button
                  className={`profile-follow-button ${
                    isFollowing ? "following" : ""
                  }`}
                  onClick={handleFollowToggle}
                  disabled={followLoading}
                >
                  {followLoading
                    ? "Loading..."
                    : isFollowing
                    ? "Following"
                    : "Follow"}
                </button>
              )}
            </div>

            {profile.display_name && (
              <p className="profile-display-name">
                {profile.display_name}
              </p>
            )}

            {profile.bio && (
              <p className="profile-bio">
                {profile.bio}
              </p>
            )}

            <div className="profile-stats">
              <span className="profile-stat">
                <strong>{profile.posts_count}</strong>
                Posts
              </span>

              <button
                className="profile-stat profile-stat-button"
                onClick={handleFollowers}
              >
                <strong>{profile.followers_count}</strong>
                Followers
              </button>

              <button
                className="profile-stat profile-stat-button"
                onClick={handleFollowing}
              >
                <strong>{profile.following_count}</strong>
                Following
              </button>
            </div>
          </div>
        </div>

        {showFollowers && (
          <div className="profile-follow-list">
            <div className="profile-follow-list-header">
              <h2>Followers</h2>
              <button onClick={() => setShowFollowers(false)}>
                Close
              </button>
            </div>

            {followers.length === 0 ? (
              <p className="profile-empty">
                No followers yet.
              </p>
            ) : (
              <div className="profile-user-list">
                {followers.map((user) => (
                  <div
                    className="profile-user-item"
                    key={user.id}
                  >
                    <Link to={`/users/${user.id}`}>
                      <strong>{user.username}</strong>
                    </Link>

                    {user.display_name && (
                      <span>{user.display_name}</span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {showFollowing && (
          <div className="profile-follow-list">
            <div className="profile-follow-list-header">
              <h2>Following</h2>
              <button onClick={() => setShowFollowing(false)}>
                Close
              </button>
            </div>

            {following.length === 0 ? (
              <p className="profile-empty">
                Not following anyone yet.
              </p>
            ) : (
              <div className="profile-user-list">
                {following.map((user) => (
                  <div
                    className="profile-user-item"
                    key={user.id}
                  >
                    <Link to={`/users/${user.id}`}>
                      <strong>{user.username}</strong>
                    </Link>

                    {user.display_name && (
                      <span>{user.display_name}</span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="profile-posts-section">
          <h2 className="profile-posts-title">
            Posts
          </h2>

          {posts.length === 0 ? (
            <p className="profile-empty">
              No posts yet.
            </p>
          ) : (
            <div className="profile-posts">
              {posts.map((post) => (
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
              ))}
            </div>
          )}
        </div>

      </div>
    </main>
  );
}

export default Profile;