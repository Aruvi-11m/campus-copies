import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import StudentLayout from './components/Student/StudentLayout';
import AdminLayout from './components/Admin/AdminLayout';
import StudentLogin from './components/Student/StudentLogin';
import AdminLogin from './components/Admin/AdminLogin';
import StudentDashboard from './components/Student/StudentDashboard';
import NewOrderWizard from './components/Student/NewOrderWizard';
import AdminDashboard from './components/Admin/AdminDashboard';
import OrderManagement from './components/Admin/OrderManagement';
import Settings from './components/Admin/Settings';
import MaterialLogs from './components/Admin/MaterialLogs';

function PrivateRoute({ children, role }) {
  const token = localStorage.getItem('token');
  const userRole = localStorage.getItem('role');
  if (!token || userRole !== role) {
    return <Navigate to={`/${role}/login`} />;
  }
  return children;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/student/login" />} />
        
        <Route path="/student/login" element={<StudentLogin />} />
        <Route path="/student" element={
          <PrivateRoute role="student">
            <StudentLayout />
          </PrivateRoute>
        }>
          <Route path="dashboard" element={<StudentDashboard />} />
          <Route path="new-order" element={<NewOrderWizard />} />
        </Route>

        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin" element={
          <PrivateRoute role="admin">
            <AdminLayout />
          </PrivateRoute>
        }>
          <Route path="dashboard" element={<AdminDashboard />} />
          <Route path="orders" element={<OrderManagement />} />
          <Route path="materials" element={<MaterialLogs />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
