import { useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";

function Search() {
  const [query, setQuery] = useState("");
  const [users, setUsers] = useState([]);
  const [posts, setPosts] = useState([]);
  const [hashtagPosts, setHashtagPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (e) => {
    e.preventDefault();

    const searchQuery = query.trim();

    if (!searchQuery) {
      setUsers([]);
      setPosts([]);
      setHashtagPosts([]);
      return;
    }

    setLoading(true);
    setError("");
    const hashtag = searchQuery.startsWith("#")
      ? searchQuery.slice(1)
      : "";

  try {
    const [usersResponse, postsResponse] = await Promise.all([
      api.get(`search/users/?q=${encodeURIComponent(searchQuery)}`),
      api.get(`search/posts/?q=${encodeURIComponent(searchQuery)}`),
    ]);

    setUsers(usersResponse.data.results || []);
    setPosts(postsResponse.data.results || []);

    if (hashtag) {
      const hashtagResponse = await api.get(
        `posts/hashtags/${encodeURIComponent(hashtag)}/`
      );

      setHashtagPosts(
        hashtagResponse.data.results || hashtagResponse.data || []
      );
    } else {
      setHashtagPosts([]);
    }
  } catch (err) {
    console.error(err);
    setError("Search failed.");
  } finally {
      setLoading(false);
    }
  };

  return (
    <main className="search-page">
      <div className="search-container">

        <div className="search-header">
          <h1>Search</h1>
          <p>Find users, posts, and hashtags</p>
        </div>

        <form className="search-form" onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="Search users or posts..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />

          <button type="submit">
            Search
          </button>
        </form>

        {loading && (
          <p className="search-status">
            Searching...
          </p>
        )}

        {error && (
          <p className="search-error">
            {error}
          </p>
        )}

        {!loading && !error && query.trim() && (
          <div className="search-results">

            <section className="search-section">
              <h2>Users</h2>

              {users.length === 0 ? (
                <p className="search-empty">
                  No users found.
                </p>
              ) : (
                <div className="search-user-list">
                  {users.map((user) => (
                    <Link
                      className="search-user"
                      key={user.id}
                      to={`/users/${user.id}`}
                    >
                      <div className="search-user-avatar">
                        {user.username?.charAt(0).toUpperCase()}
                      </div>

                      <div className="search-user-info">
                        <strong>{user.username}</strong>

                        {user.display_name && (
                          <span>{user.display_name}</span>
                        )}
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </section>

            <section className="search-section">
              <h2>Posts</h2>

              {posts.length === 0 ? (
                <p className="search-empty">
                  No posts found.
                </p>
              ) : (
                <div className="search-post-list">
                  {posts.map((post) => (
                    <Link
                      className="search-post"
                      key={post.id}
                      to={`/posts/${post.id}`}
                    >
                      <div className="search-post-content">
                        <strong>{post.author}</strong>

                        {post.caption && (
                          <p>{post.caption}</p>
                        )}

                        {post.location && (
                          <span>{post.location}</span>
                        )}
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </section>

            <section className="search-section">
              <h2>Hashtag Posts</h2>

              {hashtagPosts.length === 0 ? (
                <p className="search-empty">
                  No hashtag posts found.
                </p>
              ) : (
                <div className="search-post-list">
                  {hashtagPosts.map((post) => (
                    <Link
                      className="search-post"
                      key={post.id}
                      to={`/posts/${post.id}`}
                    >
                      <div className="search-post-content">
                        <strong>{post.author}</strong>

                        {post.caption && (
                          <p>{post.caption}</p>
                        )}

                        {post.location && (
                          <span>{post.location}</span>
                        )}
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </section>

          </div>
        )}

      </div>
    </main>
  );
}

export default Search;