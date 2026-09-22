import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    const loadNotifications = async () => {
      try {
        const response = await api.get("auth/notifications/");

        setNotifications(response.data.results || response.data);
      } catch (err) {
        console.error(err);
        setError("Failed to load notifications.");
      } finally {
        setLoading(false);
      }
    };

    loadNotifications();
  }, []);

  const handleNotificationClick = async (notification) => {
    try {
      // Mark as read
      if (!notification.is_read) {
        await api.post(
          `auth/notifications/${notification.id}/read/`
        );

        setNotifications((currentNotifications) =>
          currentNotifications.map((item) =>
            item.id === notification.id
              ? { ...item, is_read: true }
              : item
          )
        );
      }

      // Navigate based on notification type
      if (
        notification.notification_type === "like" ||
        notification.notification_type === "comment"
      ) {
        if (notification.post) {
          navigate(`/posts/${notification.post}`);
        }
      } else if (
        notification.notification_type === "follow"
      ) {
        if (notification.sender?.id) {
          navigate(`/users/${notification.sender.id}`);
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return <p>Loading notifications...</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }

  return (
    <main className="notifications-page">
      <div className="notifications-container">

        <div className="notifications-header">
          <h1>Notifications</h1>
          <p>Stay updated with your activity</p>
        </div>

        {notifications.length === 0 ? (
          <div className="notifications-empty">
            <div className="notifications-empty-icon">🔔</div>

            <h2>No notifications yet</h2>

            <p>
              You'll see likes, comments, and follows here.
            </p>
          </div>
        ) : (
          <div className="notifications-list">
            {notifications.map((notification) => (
              <button
                className={`notification-item ${
                  notification.is_read ? "read" : "unread"
                }`}
                key={notification.id}
                onClick={() =>
                  handleNotificationClick(notification)
                }
              >
                <div className="notification-icon">
                  {notification.notification_type === "like" && "❤️"}
                  {notification.notification_type === "comment" && "💬"}
                  {notification.notification_type === "follow" && "👤"}
                </div>

                <div className="notification-content">
                  <div className="notification-text">
                    <strong>
                      {notification.sender?.username}
                    </strong>

                    <span>
                      {notification.notification_type === "like" &&
                        " liked your post"}

                      {notification.notification_type === "comment" &&
                        " commented on your post"}

                      {notification.notification_type === "follow" &&
                        " started following you"}
                    </span>
                  </div>

                  {!notification.is_read && (
                    <span className="notification-new">
                      New
                    </span>
                  )}
                </div>

                {!notification.is_read && (
                  <span className="notification-dot"></span>
                )}
              </button>
            ))}
          </div>
        )}

      </div>
    </main>
  );
}

export default Notifications;