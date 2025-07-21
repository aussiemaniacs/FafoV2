import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Main Dashboard Component
const Dashboard = () => {
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching stats:", error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-white mb-8 text-center">
        🎬 FafoV2 Media Center
      </h1>
      
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6 text-center">
          <h3 className="text-xl font-semibold text-white mb-2">Total Media</h3>
          <p className="text-3xl font-bold text-blue-400">{stats.total_media_items || 0}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 text-center">
          <h3 className="text-xl font-semibold text-white mb-2">Custom Lists</h3>
          <p className="text-3xl font-bold text-green-400">{stats.total_custom_lists || 0}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 text-center">
          <h3 className="text-xl font-semibold text-white mb-2">Categories</h3>
          <p className="text-3xl font-bold text-purple-400">{Object.keys(stats.categories || {}).length}</p>
        </div>
      </div>

      {/* Category Navigation */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Link to="/movies" className="group">
          <div className="bg-gradient-to-br from-red-600 to-red-800 rounded-lg p-6 text-center hover:from-red-500 hover:to-red-700 transition-all duration-300 transform group-hover:scale-105">
            <div className="text-4xl mb-4">🎬</div>
            <h3 className="text-xl font-semibold text-white">Movies</h3>
            <p className="text-red-200">{stats.categories?.movies || 0} items</p>
          </div>
        </Link>

        <Link to="/tv-series" className="group">
          <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg p-6 text-center hover:from-blue-500 hover:to-blue-700 transition-all duration-300 transform group-hover:scale-105">
            <div className="text-4xl mb-4">📺</div>
            <h3 className="text-xl font-semibold text-white">TV Series</h3>
            <p className="text-blue-200">{stats.categories?.tv_series || 0} items</p>
          </div>
        </Link>

        <Link to="/live-tv" className="group">
          <div className="bg-gradient-to-br from-green-600 to-green-800 rounded-lg p-6 text-center hover:from-green-500 hover:to-green-700 transition-all duration-300 transform group-hover:scale-105">
            <div className="text-4xl mb-4">📡</div>
            <h3 className="text-xl font-semibold text-white">Live TV</h3>
            <p className="text-green-200">{stats.categories?.live_tv || 0} items</p>
          </div>
        </Link>

        <Link to="/youtube" className="group">
          <div className="bg-gradient-to-br from-red-500 to-red-700 rounded-lg p-6 text-center hover:from-red-400 hover:to-red-600 transition-all duration-300 transform group-hover:scale-105">
            <div className="text-4xl mb-4">▶️</div>
            <h3 className="text-xl font-semibold text-white">YouTube</h3>
            <p className="text-red-200">{stats.categories?.youtube || 0} items</p>
          </div>
        </Link>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 text-center">
        <Link
          to="/add-media"
          className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-lg mr-4 transition-colors duration-200"
        >
          ➕ Add Media
        </Link>
        <Link
          to="/custom-lists"
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-6 rounded-lg transition-colors duration-200"
        >
          📝 Custom Lists
        </Link>
      </div>
    </div>
  );
};

// Media Category Component
const MediaCategory = ({ category, title, icon }) => {
  const [media, setMedia] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMedia();
  }, [category]);

  const fetchMedia = async () => {
    try {
      const response = await axios.get(`${API}/media?category=${category}`);
      setMedia(response.data);
      setLoading(false);
    } catch (error) {
      console.error(`Error fetching ${category}:`, error);
      setLoading(false);
    }
  };

  const handlePlay = async (mediaItem) => {
    try {
      if (mediaItem.media_type === 'youtube' || mediaItem.url.includes('youtube.com') || mediaItem.url.includes('youtu.be')) {
        // Get stream URL for YouTube videos
        const response = await axios.get(`${API}/video/stream?url=${encodeURIComponent(mediaItem.url)}`);
        window.open(response.data.stream_url, '_blank');
      } else {
        // Direct link
        window.open(mediaItem.url, '_blank');
      }
    } catch (error) {
      console.error('Error playing media:', error);
      // Fallback to original URL
      window.open(mediaItem.url, '_blank');
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center">
          <span className="text-4xl mr-3">{icon}</span>
          {title}
        </h1>
        <Link
          to="/"
          className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
        >
          ← Back to Home
        </Link>
      </div>

      {media.length === 0 ? (
        <div className="text-center text-gray-400 py-16">
          <div className="text-6xl mb-4">📭</div>
          <p className="text-xl">No media items in this category yet.</p>
          <Link
            to="/add-media"
            className="inline-block mt-4 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
          >
            Add Some Content
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {media.map((item) => (
            <div key={item.id} className="bg-gray-800 rounded-lg overflow-hidden hover:bg-gray-700 transition-colors duration-200">
              {item.thumbnail && (
                <img
                  src={item.thumbnail}
                  alt={item.title}
                  className="w-full h-48 object-cover"
                />
              )}
              <div className="p-4">
                <h3 className="text-lg font-semibold text-white mb-2 truncate">{item.title}</h3>
                {item.description && (
                  <p className="text-gray-400 text-sm mb-3 line-clamp-2">{item.description}</p>
                )}
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-500 bg-gray-700 px-2 py-1 rounded">
                    {item.media_type}
                  </span>
                  <button
                    onClick={() => handlePlay(item)}
                    className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded text-sm transition-colors duration-200"
                  >
                    ▶️ Play
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Add Media Component
const AddMedia = () => {
  const [formData, setFormData] = useState({
    title: '',
    url: '',
    media_type: 'direct_link',
    category: 'movies',
    description: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [videoInfo, setVideoInfo] = useState(null);

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const fetchVideoInfo = async () => {
    if (!formData.url) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API}/video/info?url=${encodeURIComponent(formData.url)}`);
      setVideoInfo(response.data);
      setFormData({
        ...formData,
        title: response.data.title || formData.title,
        description: response.data.title || formData.description
      });
      setMessage('Video info loaded successfully!');
    } catch (error) {
      console.error('Error fetching video info:', error);
      setMessage('Could not fetch video info. You can still add it manually.');
    }
    setLoading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      await axios.post(`${API}/media`, formData);
      setMessage('Media item added successfully!');
      setFormData({
        title: '',
        url: '',
        media_type: 'direct_link',
        category: 'movies',
        description: ''
      });
      setVideoInfo(null);
    } catch (error) {
      console.error('Error adding media:', error);
      setMessage('Error adding media item. Please try again.');
    }
    setLoading(false);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-white">➕ Add Media</h1>
        <Link
          to="/"
          className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
        >
          ← Back to Home
        </Link>
      </div>

      <div className="bg-gray-800 rounded-lg p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-white text-sm font-bold mb-2">
              Media URL
            </label>
            <div className="flex gap-2">
              <input
                type="url"
                name="url"
                value={formData.url}
                onChange={handleInputChange}
                className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:border-blue-500"
                placeholder="https://youtube.com/watch?v=... or direct video link"
                required
              />
              <button
                type="button"
                onClick={fetchVideoInfo}
                disabled={loading || !formData.url}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded transition-colors duration-200"
              >
                {loading ? '...' : '🔍'}
              </button>
            </div>
          </div>

          {videoInfo && (
            <div className="bg-gray-700 rounded p-4">
              <h3 className="text-white font-semibold mb-2">Video Info Preview:</h3>
              <p className="text-gray-300 text-sm">Title: {videoInfo.title}</p>
              {videoInfo.duration && (
                <p className="text-gray-300 text-sm">Duration: {Math.floor(videoInfo.duration / 60)}m {videoInfo.duration % 60}s</p>
              )}
              {videoInfo.quality && (
                <p className="text-gray-300 text-sm">Quality: {videoInfo.quality}</p>
              )}
            </div>
          )}

          <div>
            <label className="block text-white text-sm font-bold mb-2">
              Title
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:border-blue-500"
              placeholder="Media title"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-white text-sm font-bold mb-2">
                Media Type
              </label>
              <select
                name="media_type"
                value={formData.media_type}
                onChange={handleInputChange}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:border-blue-500"
              >
                <option value="direct_link">Direct Link</option>
                <option value="youtube">YouTube</option>
                <option value="playlist">Playlist</option>
                <option value="live_tv">Live TV</option>
              </select>
            </div>

            <div>
              <label className="block text-white text-sm font-bold mb-2">
                Category
              </label>
              <select
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:border-blue-500"
              >
                <option value="movies">Movies</option>
                <option value="tv_series">TV Series</option>
                <option value="live_tv">Live TV</option>
                <option value="youtube">YouTube</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-white text-sm font-bold mb-2">
              Description (Optional)
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:border-blue-500 h-24"
              placeholder="Brief description..."
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-bold py-3 px-4 rounded transition-colors duration-200"
          >
            {loading ? 'Adding...' : 'Add Media Item'}
          </button>
        </form>

        {message && (
          <div className={`mt-4 p-3 rounded ${message.includes('Error') ? 'bg-red-900 text-red-200' : 'bg-green-900 text-green-200'}`}>
            {message}
          </div>
        )}
      </div>
    </div>
  );
};

// Custom Lists Component
const CustomLists = () => {
  const [lists, setLists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newListName, setNewListName] = useState('');
  const [newListDescription, setNewListDescription] = useState('');

  useEffect(() => {
    fetchLists();
  }, []);

  const fetchLists = async () => {
    try {
      const response = await axios.get(`${API}/lists`);
      setLists(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching lists:', error);
      setLoading(false);
    }
  };

  const createList = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/lists`, {
        name: newListName,
        description: newListDescription
      });
      setNewListName('');
      setNewListDescription('');
      setShowCreateForm(false);
      fetchLists();
    } catch (error) {
      console.error('Error creating list:', error);
    }
  };

  const deleteList = async (listId) => {
    if (window.confirm('Are you sure you want to delete this list?')) {
      try {
        await axios.delete(`${API}/lists/${listId}`);
        fetchLists();
      } catch (error) {
        console.error('Error deleting list:', error);
      }
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center">
          <span className="text-4xl mr-3">📝</span>
          Custom Lists
        </h1>
        <div className="space-x-4">
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
          >
            ➕ New List
          </button>
          <Link
            to="/"
            className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
          >
            ← Back to Home
          </Link>
        </div>
      </div>

      {showCreateForm && (
        <div className="bg-gray-800 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">Create New List</h2>
          <form onSubmit={createList} className="space-y-4">
            <input
              type="text"
              value={newListName}
              onChange={(e) => setNewListName(e.target.value)}
              placeholder="List name"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:border-blue-500"
              required
            />
            <textarea
              value={newListDescription}
              onChange={(e) => setNewListDescription(e.target.value)}
              placeholder="List description (optional)"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:border-blue-500 h-24"
            />
            <div className="flex space-x-4">
              <button
                type="submit"
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
              >
                Create List
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {lists.length === 0 ? (
        <div className="text-center text-gray-400 py-16">
          <div className="text-6xl mb-4">📝</div>
          <p className="text-xl">No custom lists created yet.</p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="inline-block mt-4 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
          >
            Create Your First List
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {lists.map((list) => (
            <div key={list.id} className="bg-gray-800 rounded-lg p-6">
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-xl font-semibold text-white">{list.name}</h3>
                <button
                  onClick={() => deleteList(list.id)}
                  className="text-red-400 hover:text-red-300 text-sm"
                >
                  🗑️
                </button>
              </div>
              {list.description && (
                <p className="text-gray-400 text-sm mb-4">{list.description}</p>
              )}
              <div className="flex justify-between items-center text-sm text-gray-400">
                <span>{list.items.length} items</span>
                <span>{new Date(list.created_at).toLocaleDateString()}</span>
              </div>
              <Link
                to={`/lists/${list.id}`}
                className="block mt-4 text-center bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors duration-200"
              >
                View List
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Main App Component
function App() {
  return (
    <div className="App min-h-screen bg-gray-900">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/movies" element={<MediaCategory category="movies" title="Movies" icon="🎬" />} />
          <Route path="/tv-series" element={<MediaCategory category="tv_series" title="TV Series" icon="📺" />} />
          <Route path="/live-tv" element={<MediaCategory category="live_tv" title="Live TV" icon="📡" />} />
          <Route path="/youtube" element={<MediaCategory category="youtube" title="YouTube" icon="▶️" />} />
          <Route path="/add-media" element={<AddMedia />} />
          <Route path="/custom-lists" element={<CustomLists />} />
          <Route path="/lists/:listId" element={<CustomLists />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;