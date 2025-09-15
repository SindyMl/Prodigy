import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import { initializeApp } from 'firebase/app';
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut, onAuthStateChanged } from 'firebase/auth';
import { QueryClient, QueryClientProvider, useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import './App.css';

// Firebase config
const firebaseConfig = {
  apiKey: "AIzaSyBr_ioDQft7Qkb8UkBxKupi45AZgphuz14",
  authDomain: "prodigy-8682a.firebaseapp.com",
  projectId: "prodigy-8682a",
  storageBucket: "prodigy-8682a.firebasestorage.app",
  messagingSenderId: "920783433866",
  appId: "1:920783433866:web:cd6f8d72632a6ec0927d73",
  measurementId: "G-CJX69ZQS46"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Create Query Client
const queryClient = new QueryClient();

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // For demo purposes, check if user is already logged in via localStorage
    const savedUser = localStorage.getItem('prodigy_user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      // For demo purposes, create a mock user
      const mockUser = {
        uid: `user_${Date.now()}`,
        email: email,
        displayName: email.split('@')[0],
        token: `mock_user_${Date.now()}`
      };
      setUser(mockUser);
      localStorage.setItem('prodigy_user', JSON.stringify(mockUser));
      return { user: mockUser };
    } catch (error) {
      throw new Error('Login failed');
    }
  };

  const register = async (email, password) => {
    try {
      // For demo purposes, create a mock user
      const mockUser = {
        uid: `user_${Date.now()}`,
        email: email,
        displayName: email.split('@')[0],
        token: `mock_user_${Date.now()}`
      };
      setUser(mockUser);
      localStorage.setItem('prodigy_user', JSON.stringify(mockUser));
      return { user: mockUser };
    } catch (error) {
      throw new Error('Registration failed');
    }
  };

  const logout = async () => {
    setUser(null);
    localStorage.removeItem('prodigy_user');
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => useContext(AuthContext);

// API Helper - Fixed for mutations
const createApiCall = (user) => {
  return async (endpoint, options = {}) => {
    const config = {
      url: `${API}${endpoint}`,
      method: 'GET',
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(user?.token && { Authorization: `Bearer ${user.token}` }),
        ...options.headers
      }
    };
    
    const response = await axios(config);
    return response.data;
  };
};

// Components
const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return children;

  return (
    <div className="min-h-screen bg-gray-800 text-gray-100">
      <nav className="bg-violet-700 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex space-x-6">
            <Link to="/" className="text-xl font-bold">Prodigy</Link>
            <Link to="/" className="hover:text-violet-200">Dashboard</Link>
            <Link to="/study" className="hover:text-violet-200">Study</Link>
            <Link to="/work" className="hover:text-violet-200">Work</Link>
            <Link to="/calendar" className="hover:text-violet-200">Calendar</Link>
          </div>
          <div className="flex items-center space-x-4">
            <span>{user.email}</span>
            <button onClick={logout} className="bg-red-600 px-3 py-1 rounded hover:bg-red-700">
              Logout
            </button>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto p-6">
        {children}
      </main>
    </div>
  );
};

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) return <div className="flex justify-center items-center min-h-screen bg-gray-800 text-white">Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  
  return children;
};

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState('');
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (isRegister) {
        await register(email, password);
      } else {
        await login(email, password);
      }
      navigate('/');
    } catch (error) {
      setError(error.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-800 flex items-center justify-center">
      <div className="bg-gray-700 p-8 rounded-lg shadow-lg w-96">
        <h1 className="text-3xl font-bold text-center text-violet-400 mb-6">
          {isRegister ? 'Register' : 'Login'} to Prodigy
        </h1>
        {error && <div className="bg-red-600 text-white p-3 rounded mb-4">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-3 bg-gray-600 text-white rounded border border-gray-500 focus:border-violet-500"
              required
            />
          </div>
          <div className="mb-6">
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-3 bg-gray-600 text-white rounded border border-gray-500 focus:border-violet-500"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-violet-600 text-white p-3 rounded hover:bg-violet-700"
          >
            {isRegister ? 'Register' : 'Login'}
          </button>
        </form>
        <p className="text-center mt-4 text-gray-300">
          {isRegister ? 'Already have an account?' : "Don't have an account?"}
          <button
            onClick={() => setIsRegister(!isRegister)}
            className="text-violet-400 ml-2 hover:underline"
          >
            {isRegister ? 'Login' : 'Register'}
          </button>
        </p>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const { user } = useAuth();
  
  const { data: quote } = useQuery({ queryKey: ['quote'], queryFn: () => apiCall('/quote') });
  const { data: todayEvents } = useQuery({ queryKey: ['todayEvents'], queryFn: () => apiCall('/events/today') });

  return (
    <div className="space-y-6">
      <h1 className="text-4xl font-bold text-center">Welcome back, {user?.displayName || 'User'}!</h1>
      
      {/* Motivational Quote */}
      <div className="bg-gradient-to-r from-violet-700 to-blue-600 p-6 rounded-lg">
        <h2 className="text-2xl font-semibold mb-3">Daily Inspiration</h2>
        {quote && (
          <blockquote className="text-lg italic">
            "{quote.quote}" - {quote.author}
          </blockquote>
        )}
      </div>

      {/* Today's Agenda */}
      <div className="bg-gray-700 p-6 rounded-lg">
        <h2 className="text-2xl font-semibold mb-3">Today's Agenda</h2>
        {todayEvents && todayEvents.length > 0 ? (
          <ul className="space-y-2">
            {todayEvents.map((event) => (
              <li key={event.id} className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${
                  event.event_type === 'study' ? 'bg-blue-500' :
                  event.event_type === 'work' ? 'bg-orange-500' : 'bg-green-500'
                }`}></div>
                <span>{event.title} - {new Date(event.datetime).toLocaleTimeString()}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-400">No events scheduled for today</p>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link to="/study" className="bg-blue-600 p-6 rounded-lg hover:bg-blue-700 text-center">
          <h3 className="text-xl font-semibold">Start Study Session</h3>
          <p className="text-gray-200">Pomodoro timer & flashcards</p>
        </Link>
        <Link to="/work" className="bg-orange-600 p-6 rounded-lg hover:bg-orange-700 text-center">
          <h3 className="text-xl font-semibold">Manage Projects</h3>
          <p className="text-gray-200">Kanban boards & tasks</p>
        </Link>
        <Link to="/calendar" className="bg-green-600 p-6 rounded-lg hover:bg-green-700 text-center">
          <h3 className="text-xl font-semibold">View Calendar</h3>
          <p className="text-gray-200">Schedule & events</p>
        </Link>
      </div>
    </div>
  );
};

const PomodoroTimer = () => {
  const [timeLeft, setTimeLeft] = useState(25 * 60); // 25 minutes
  const [isRunning, setIsRunning] = useState(false);
  const [isBreak, setIsBreak] = useState(false);

  useEffect(() => {
    let interval = null;
    if (isRunning && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft(timeLeft => timeLeft - 1);
      }, 1000);
    } else if (timeLeft === 0) {
      setIsRunning(false);
      setIsBreak(!isBreak);
      setTimeLeft(isBreak ? 25 * 60 : 5 * 60);
    }
    return () => clearInterval(interval);
  }, [isRunning, timeLeft, isBreak]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-gray-700 p-6 rounded-lg text-center">
      <h3 className="text-2xl font-semibold mb-4">
        {isBreak ? 'Break Time!' : 'Focus Time'}
      </h3>
      <div className="text-6xl font-mono mb-6">{formatTime(timeLeft)}</div>
      <div className="space-x-4">
        <button
          onClick={() => setIsRunning(!isRunning)}
          className="bg-blue-600 px-6 py-2 rounded hover:bg-blue-700"
        >
          {isRunning ? 'Pause' : 'Start'}
        </button>
        <button
          onClick={() => {
            setTimeLeft(isBreak ? 5 * 60 : 25 * 60);
            setIsRunning(false);
          }}
          className="bg-gray-600 px-6 py-2 rounded hover:bg-gray-500"
        >
          Reset
        </button>
        <button
          onClick={() => {
            setIsBreak(!isBreak);
            setTimeLeft(isBreak ? 25 * 60 : 5 * 60);
            setIsRunning(false);
          }}
          className="bg-orange-600 px-6 py-2 rounded hover:bg-orange-700"
        >
          Skip
        </button>
      </div>
    </div>
  );
};

const StudySession = () => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [eventTitle, setEventTitle] = useState('');
  const [eventDateTime, setEventDateTime] = useState('');
  
  const queryClient = useQueryClient();
  
  const { data: flashcards } = useQuery({ queryKey: ['flashcards'], queryFn: () => apiCall('/flashcards') });
  
  const createFlashcard = useMutation({
    mutationFn: (data) => apiCall('/flashcards', { method: 'POST', data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['flashcards'] });
      setQuestion('');
      setAnswer('');
    }
  });
  
  const createEvent = useMutation({
    mutationFn: (data) => apiCall('/events', { method: 'POST', data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todayEvents'] });
      setEventTitle('');
      setEventDateTime('');
    }
  });

  const handleFlashcardSubmit = (e) => {
    e.preventDefault();
    createFlashcard.mutate({ question, answer });
  };

  const handleEventSubmit = (e) => {
    e.preventDefault();
    createEvent.mutate({
      title: eventTitle,
      event_type: 'study',
      datetime: new Date(eventDateTime).toISOString(),
      duration: 60
    });
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Study Session</h1>
      
      <PomodoroTimer />
      
      {/* Flashcard Creator */}
      <div className="bg-gray-700 p-6 rounded-lg">
        <h2 className="text-2xl font-semibold mb-4">Create Flashcard</h2>
        <form onSubmit={handleFlashcardSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Question</label>
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="w-full p-3 bg-gray-600 rounded border border-gray-500 focus:border-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Answer</label>
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              rows="3"
              className="w-full p-3 bg-gray-600 rounded border border-gray-500 focus:border-blue-500"
              required
            />
          </div>
          <button
            type="submit"
            disabled={createFlashcard.isLoading}
            className="bg-blue-600 px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {createFlashcard.isLoading ? 'Creating...' : 'Create Flashcard'}
          </button>
        </form>
      </div>

      {/* Schedule Study Event */}
      <div className="bg-gray-700 p-6 rounded-lg">
        <h2 className="text-2xl font-semibold mb-4">Schedule Study Session</h2>
        <form onSubmit={handleEventSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Title</label>
            <input
              type="text"
              value={eventTitle}
              onChange={(e) => setEventTitle(e.target.value)}
              className="w-full p-3 bg-gray-600 rounded border border-gray-500 focus:border-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Date & Time</label>
            <input
              type="datetime-local"
              value={eventDateTime}
              onChange={(e) => setEventDateTime(e.target.value)}
              className="w-full p-3 bg-gray-600 rounded border border-gray-500 focus:border-blue-500"
              required
            />
          </div>
          <button
            type="submit"
            disabled={createEvent.isLoading}
            className="bg-blue-600 px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {createEvent.isLoading ? 'Scheduling...' : 'Schedule Event'}
          </button>
        </form>
      </div>

      {/* Flashcards List */}
      <div className="bg-gray-700 p-6 rounded-lg">
        <h2 className="text-2xl font-semibold mb-4">Your Flashcards</h2>
        {flashcards && flashcards.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {flashcards.map((card) => (
              <div key={card.id} className="bg-gray-600 p-4 rounded">
                <div className="font-semibold mb-2">Q: {card.question}</div>
                <div className="text-gray-300">A: {card.answer}</div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400">No flashcards created yet</p>
        )}
      </div>
    </div>
  );
};

const KanbanBoard = ({ projectId }) => {
  const queryClient = useQueryClient();
  const { data: tasks = [] } = useQuery({ queryKey: ['tasks', projectId], queryFn: () => apiCall(`/projects/${projectId}/tasks`) });
  
  const updateTask = useMutation({
    mutationFn: ({ taskId, ...data }) => apiCall(`/tasks/${taskId}`, { method: 'PUT', data }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks', projectId] })
  });

  const columns = {
    backlog: { title: 'Backlog', color: 'bg-gray-600' },
    todo: { title: 'To Do', color: 'bg-blue-600' },
    in_progress: { title: 'In Progress', color: 'bg-orange-600' },
    done: { title: 'Done', color: 'bg-green-600' }
  };

  const getTasksByStatus = (status) => tasks.filter(task => task.status === status);

  const onDragEnd = (result) => {
    if (!result.destination) return;

    const { draggableId, destination } = result;
    const taskId = draggableId;
    const newStatus = destination.droppableId;

    updateTask.mutate({ taskId, status: newStatus });
  };

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {Object.entries(columns).map(([status, { title, color }]) => (
          <div key={status} className="bg-gray-700 p-4 rounded-lg">
            <h3 className={`text-lg font-semibold mb-4 p-2 rounded ${color}`}>{title}</h3>
            <Droppable droppableId={status}>
              {(provided) => (
                <div
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  className="min-h-[200px] space-y-2"
                >
                  {getTasksByStatus(status).map((task, index) => (
                    <Draggable key={task.id} draggableId={task.id} index={index}>
                      {(provided) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          className="bg-gray-600 p-3 rounded shadow cursor-move hover:bg-gray-500"
                        >
                          <div className="font-medium">{task.title}</div>
                          {task.description && (
                            <div className="text-sm text-gray-300 mt-1">{task.description}</div>
                          )}
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </div>
        ))}
      </div>
    </DragDropContext>
  );
};

const WorkSession = () => {
  const [selectedProject, setSelectedProject] = useState(null);
  const [showProjectForm, setShowProjectForm] = useState(false);
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [projectTitle, setProjectTitle] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [taskTitle, setTaskTitle] = useState('');
  const [taskDescription, setTaskDescription] = useState('');
  
  const queryClient = useQueryClient();
  
  const { data: projects = [] } = useQuery({ queryKey: ['projects'], queryFn: () => apiCall('/projects') });
  
  const createProject = useMutation({
    mutationFn: (data) => apiCall('/projects', { method: 'POST', data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setProjectTitle('');
      setProjectDescription('');
      setShowProjectForm(false);
    }
  });
  
  const createTask = useMutation({
    mutationFn: (data) => apiCall(`/projects/${selectedProject.id}/tasks`, { method: 'POST', data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', selectedProject.id] });
      setTaskTitle('');
      setTaskDescription('');
      setShowTaskForm(false);
    }
  });

  const handleProjectSubmit = (e) => {
    e.preventDefault();
    createProject.mutate({ title: projectTitle, description: projectDescription });
  };

  const handleTaskSubmit = (e) => {
    e.preventDefault();
    createTask.mutate({ title: taskTitle, description: taskDescription });
  };

  if (selectedProject) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <button
              onClick={() => setSelectedProject(null)}
              className="text-violet-400 hover:underline mb-2"
            >
              ← Back to Projects
            </button>
            <h1 className="text-3xl font-bold">{selectedProject.title}</h1>
            <p className="text-gray-400">{selectedProject.description}</p>
          </div>
          <button
            onClick={() => setShowTaskForm(true)}
            className="bg-orange-600 px-4 py-2 rounded hover:bg-orange-700"
          >
            Add Task
          </button>
        </div>

        {showTaskForm && (
          <div className="bg-gray-700 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Create New Task</h2>
            <form onSubmit={handleTaskSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Title</label>
                <input
                  type="text"
                  value={taskTitle}
                  onChange={(e) => setTaskTitle(e.target.value)}
                  className="w-full p-3 bg-gray-600 rounded border border-gray-500 focus:border-orange-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Description</label>
                <textarea
                  value={taskDescription}
                  onChange={(e) => setTaskDescription(e.target.value)}
                  rows="3"
                  className="w-full p-3 bg-gray-600 rounded border border-gray-500 focus:border-orange-500"
                />
              </div>
              <div className="flex space-x-4">
                <button
                  type="submit"
                  disabled={createTask.isLoading}
                  className="bg-orange-600 px-6 py-2 rounded hover:bg-orange-700 disabled:opacity-50"
                >
                  {createTask.isLoading ? 'Creating...' : 'Create Task'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowTaskForm(false)}
                  className="bg-gray-600 px-6 py-2 rounded hover:bg-gray-500"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        <KanbanBoard projectId={selectedProject.id} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Work Projects</h1>
        <button
          onClick={() => setShowProjectForm(true)}
          className="bg-orange-600 px-4 py-2 rounded hover:bg-orange-700"
        >
          New Project
        </button>
      </div>

      {showProjectForm && (
        <div className="bg-gray-700 p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Create New Project</h2>
          <form onSubmit={handleProjectSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Title</label>
              <input
                type="text"
                value={projectTitle}
                onChange={(e) => setProjectTitle(e.target.value)}
                className="w-full p-3 bg-gray-600 rounded border border-gray-500 focus:border-orange-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Description</label>
              <textarea
                value={projectDescription}
                onChange={(e) => setProjectDescription(e.target.value)}
                rows="3"
                className="w-full p-3 bg-gray-600 rounded border border-gray-500 focus:border-orange-500"
              />
            </div>
            <div className="flex space-x-4">
              <button
                type="submit"
                disabled={createProject.isLoading}
                className="bg-orange-600 px-6 py-2 rounded hover:bg-orange-700 disabled:opacity-50"
              >
                {createProject.isLoading ? 'Creating...' : 'Create Project'}
              </button>
              <button
                type="button"
                onClick={() => setShowProjectForm(false)}
                className="bg-gray-600 px-6 py-2 rounded hover:bg-gray-500"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((project) => (
          <div
            key={project.id}
            onClick={() => setSelectedProject(project)}
            className="bg-gray-700 p-6 rounded-lg cursor-pointer hover:bg-gray-600 transition-colors"
          >
            <h3 className="text-xl font-semibold mb-2">{project.title}</h3>
            <p className="text-gray-400 mb-4">{project.description || 'No description'}</p>
            <div className="text-sm text-gray-500">
              Created: {new Date(project.created_at).toLocaleDateString()}
            </div>
          </div>
        ))}
      </div>

      {projects.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-400 text-lg">No projects yet. Create your first project to get started!</p>
        </div>
      )}
    </div>
  );
};

const Calendar = () => {
  const { data: events = [] } = useQuery({ queryKey: ['events'], queryFn: () => apiCall('/events') });

  const calendarEvents = events.map(event => ({
    id: event.id,
    title: event.title,
    date: new Date(event.datetime).toISOString().split('T')[0],
    color: event.event_type === 'study' ? '#2563eb' : 
           event.event_type === 'work' ? '#ea580c' : '#059669'
  }));

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Calendar</h1>
      
      <div className="bg-white p-4 rounded-lg">
        <FullCalendar
          plugins={[dayGridPlugin]}
          initialView="dayGridMonth"
          events={calendarEvents}
          headerToolbar={{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,dayGridWeek'
          }}
          height="auto"
        />
      </div>
    </div>
  );
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <div className="App">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/*" element={
                <ProtectedRoute>
                  <Layout>
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/study" element={<StudySession />} />
                      <Route path="/work" element={<WorkSession />} />
                      <Route path="/calendar" element={<Calendar />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              } />
            </Routes>
          </div>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;