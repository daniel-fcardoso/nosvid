# Nosvid

## Description

Nosvid is a video-sharing web application built with Django and JavaScript as my final project for CS50's Web Programming with Python and JavaScript.

The idea behind Nosvid actually started several years before I learned web development. When I was younger, two friends and I had the idea of creating a Brazilian video-sharing platform. At that time, none of us knew how to program, so the project never became an actual application. We only created some social media accounts and discussed what the platform could eventually become.

Years later, after learning Python, Django, JavaScript, HTML, CSS, SQL, Git, and other web development concepts, I decided to revisit that old idea and finally turn it into a working application for my CS50W final project.

The name "Nosvid" comes from the Portuguese expression "Nossos Vídeos", which means "Our Videos". The goal of the application is to provide a platform where users can create channels, upload videos, discover content, interact with other users, organize videos into playlists, and manage their own content.

Nosvid was visually inspired by YouTube and other modern video platforms, especially in its approach to video discovery, channel pages, watch pages, and content organization. However, the application implements its own backend structure, models, interactions, content management system, and user experience.

## Distinctiveness and Complexity

Nosvid is distinct from the previous CS50W projects because its main purpose is video hosting, video consumption, and video content management. Although Nosvid contains social features such as likes, comments, replies, and subscriptions, those features support the main video platform rather than being the primary purpose of the application.

In particular, Nosvid is not designed around short text posts or a social feed similar to Project 4. The central objects in the application are videos and channels. Users upload actual video files and thumbnails, videos are displayed using a media player, views are recorded, users can maintain watch history, save content for later, organize videos into playlists, browse categories, discover related videos, and manage uploaded content through a dedicated Studio interface.

The video system required several pieces of logic beyond a normal CRUD application. Each uploaded video belongs to a channel and contains a title, description, video file, optional thumbnail, category, upload date, and view count. File uploads are validated for allowed formats and file sizes. View counting also includes logic intended to avoid repeatedly increasing the counter when the same viewer refreshes the page within a short period.

Nosvid also contains a content discovery system. Videos are assigned categories such as Music, Gaming, Technology, Education, Entertainment, Sports, News, Film and Animation, People and Blogs, and Other. Search supports multiple filters, including category, channel, upload period, minimum number of views, and sorting by recent or most viewed content. The watch page also displays related videos, prioritizing videos in the same category.

Channels contain their own content and statistics. Each channel has its own page with separate Videos, Playlists, and About sections. The channel page displays subscriber count, number of uploaded videos, and total views. Users can subscribe to other channels, while the sidebar displays channels to which the current user is subscribed.

The playlist system contains additional management features. Users can create playlists, add and remove videos, choose whether a playlist is public or private, and reorder the videos inside a playlist. Private playlists can only be accessed by their owners, while public playlists can be viewed by other users.

Nosvid also implements user activity features including watch history and Watch Later. History is updated when authenticated users watch videos. Users may remove individual entries or clear their entire history. Watch Later provides a separate collection where videos can be saved and removed.

Interaction with videos includes likes and dislikes, while comments support likes, dislikes, replies, editing, and deletion. Users may also edit or delete their own replies. Permissions are enforced on the backend so that one user cannot edit or delete content belonging to another user.

Another feature is the notification system. Users can receive notifications when somebody subscribes to their channel, comments on one of their videos, replies to one of their comments, or likes one of their videos. Notifications are displayed in a popup panel in the application header and include unread state management and an option to mark notifications as read.

Finally, Nosvid includes a simple Studio interface for channel owners. The Studio gives users a centralized place to view their uploaded videos, categories, view counts, dates, and actions for editing or deleting content.

The project combines Django models and relationships, authentication, file uploads, media handling, server-side validation, permissions, database queries, pagination, JavaScript fetch requests, asynchronous user interactions, CSRF protection, responsive design, theme persistence, and dynamic interface components. Because these systems interact with each other throughout the application, the project required considerably more than implementing a single CRUD workflow.

## Features

Nosvid includes the following main features:

- User registration, login, and logout
- Channel creation and editing
- Channel avatars and descriptions
- Video uploading with thumbnails
- Video categories
- Video editing and deletion
- HTML5 video playback
- Video view counting
- Likes and dislikes
- Comments and comment reactions
- Comment replies
- Editing and deleting comments and replies
- Channel subscriptions
- Subscription feed
- Watch history
- Individual history removal
- Complete history clearing
- Watch Later
- Public and private playlists
- Playlist video reordering
- Liked videos page
- Advanced search and filtering
- Related video recommendations
- Channel statistics
- Channel tabs for Videos, Playlists, and About
- Nosvid Studio
- Notification system
- Pagination
- Light, dark, and system themes
- Responsive interface
- Custom 404 page
- Toast feedback messages
- Expandable video descriptions
- Backend permission checks
- CSRF protection
- Upload validation

## Technologies

- Python
- Django
- JavaScript
- HTML
- CSS
- SQLite
- Pillow

## Project Files

### `manage.py`

Django's command-line utility used to run the development server, migrations, and other Django management commands.

### `nosvid/settings.py`

Contains the main Django project configuration, installed applications, database configuration, static and media file configuration, template settings, and trusted origins used during development.

### `nosvid/urls.py`

Contains the root URL configuration and connects the main project to the URLs provided by the `videos` application.

### `videos/models.py`

Contains the database models used by Nosvid. These include users, channels, videos, video views, likes, dislikes, comments, comment reactions, replies, subscriptions, watch history, Watch Later entries, playlists, playlist items, and notifications.

### `videos/views.py`

Contains the majority of the backend application logic. It handles authentication, channels, video uploads and editing, search, video playback, reactions, comments, replies, subscriptions, history, playlists, notifications, related videos, Studio functionality, and permissions.

### `videos/urls.py`

Defines the routes for the `videos` application and maps URLs to their corresponding Django views.

### `videos/admin.py`

Registers application models with the Django administration interface.

### `videos/context_processors.py`

Provides global information needed by templates, particularly unread notifications and channel subscriptions displayed in the application layout.

### `videos/templates/videos/layout.html`

Provides the main shared structure of the application, including the header, search bar, sidebar, settings panel, notification panel, and theme-related interface.

### `videos/templates/videos/index.html`

Displays the Nosvid home page and the main video grid.

### `videos/templates/videos/watch.html`

Displays an individual video, its player, information, reactions, channel information, description, comments, replies, playlists, and related videos.

### `videos/templates/videos/channel.html`

Displays channel information and the Videos, Playlists, and About tabs.

### `videos/templates/videos/upload.html`

Contains the form for uploading a new video, thumbnail, description, and category.

### `videos/templates/videos/edit_video.html`

Allows channel owners to modify their existing videos.

### `videos/templates/videos/search.html`

Displays search results and provides advanced filters for category, channel, date, views, and sorting.

### `videos/templates/videos/history.html`

Displays the authenticated user's video watch history.

### `videos/templates/videos/watch_later.html`

Displays videos the user has saved to watch later.

### `videos/templates/videos/liked_videos.html`

Displays videos liked by the current user.

### `videos/templates/videos/subscriptions.html`

Displays videos uploaded by channels the current user follows.

### Playlist templates

The playlist templates handle listing playlists, creating playlists, editing them, deleting them, displaying playlist contents, controlling privacy, and rearranging videos.

### Comment templates

Templates related to comments allow users to edit their comments and replies.

### `videos/templates/videos/studio.html`

Provides the Nosvid Studio interface for managing videos uploaded to the current user's channel.

### `videos/templates/404.html`

Displays a custom page when a requested resource cannot be found.

### `videos/static/videos/styles.css`

Contains the application's responsive styling, light and dark themes, layouts, video grids, channel interface, forms, notification popup, Studio, and other visual components.

### `videos/static/videos/script.js`

Contains the client-side JavaScript used for asynchronous likes, dislikes, subscriptions, Watch Later actions, notifications, theme management, sidebar behavior, upload validation, CSRF handling, description expansion, and other interactive elements.

## How to Run

First, install the required Python packages:

```bash
pip install -r requirements.txt
```

Apply the database migrations:

```bash
python manage.py migrate
```

Then start the Django development server:

```bash
python manage.py runserver
```

Open the address provided by Django in a web browser.

Users can create an account and then create a channel. Once a channel exists, videos can be uploaded through the upload page or the Studio interface.

## Additional Information

Nosvid uses uploaded media files for videos, thumbnails, channel avatars, and other user-generated content. The application was developed and tested using Django's development environment.

The interface supports light, dark, and system-based themes. Theme preference is stored in the browser so it can remain selected between page loads.

Several actions use JavaScript and Django endpoints instead of requiring complete page reloads, including video reactions, subscriptions, Watch Later, and notification-related interactions.

The application also includes validation and ownership checks to ensure that users can only edit or delete resources they are authorized to modify.

## Video Demonstration

A demonstration video of Nosvid can be found here:

`https://youtu.be/jVA39fr2BNA`
