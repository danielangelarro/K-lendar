import { useEffect, useState } from 'react';
import { Route, Routes, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuthContext } from './context/AuthContext';

import Loader from './common/Loader';
import PageTitle from './components/PageTitle';
import SignIn from './pages/Authentication/SignIn';
import SignUp from './pages/Authentication/SignUp';
import Calendar from './pages/Calendar';
import FormElements from './pages/Form/FormElements';
import Profile from './pages/Profile';
import Alerts from './pages/UiElements/Alerts';
import Buttons from './pages/UiElements/Buttons';
import DefaultLayout from './layout/DefaultLayout';
import Group from './pages/Group';
import TaskPage from './pages/Task';
import Notifications from './components/Notificationes/Notifications';
import TimeLine from './pages/TimeLine/TimeLine'

const ProtectedRoute = ({ element }: { element: JSX.Element }) => {
  const { isAuthenticated } = useAuthContext();
  return isAuthenticated ? element : <Navigate to="/auth/signin" />;
};

const PublicRoute = ({ element, restricted }: { element: JSX.Element, restricted?: boolean }) => {
  const { isAuthenticated } = useAuthContext();
  return isAuthenticated && restricted ? <Navigate to="/" /> : element;
};

function App() {
  const [loading, setLoading] = useState<boolean>(true);
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  useEffect(() => {
    setTimeout(() => setLoading(false), 1000);
  }, []);

  return loading ? (
    <Loader />
  ) : (
    <AuthProvider>
        <Routes>
          <Route
            path="/"
            element={
              <DefaultLayout>
                <PageTitle title="Calendar | TailAdmin - Tailwind CSS Admin Dashboard Template" />
                <ProtectedRoute element={<Calendar />} />
              </DefaultLayout>
            }
          />
          <Route
            path="/group"
            element={
              <DefaultLayout>
                <PageTitle title="Group | TailAdmin - Tailwind CSS Admin Dashboard Template" />
                <ProtectedRoute element={<Group />} />
              </DefaultLayout>
            }
          />
          <Route
            path="/notification"
            element={
              <DefaultLayout>
                <PageTitle title="Notificationes | TailAdmin - Tailwind CSS Admin Dashboard Template" />
                <ProtectedRoute element={<Notifications items={[]} />} />
              </DefaultLayout>
            }
          />
          <Route
            path="/timeline"
            element={
              <DefaultLayout>
                <PageTitle title="Group | TailAdmin - Tailwind CSS Admin Dashboard Template" />
                <ProtectedRoute element={<TimeLine />} />
              </DefaultLayout>
            }
          />
          <Route
            path="/calendar"
            element={
              <DefaultLayout>
                <PageTitle title="Calendar | TailAdmin - Tailwind CSS Admin Dashboard Template" />
                <ProtectedRoute element={<Calendar />} />
              </DefaultLayout>
            }
          />
          <Route
            path="/profile"
            element={
              <DefaultLayout>
                <PageTitle title="Profile | TailAdmin - Tailwind CSS Admin Dashboard Template" />
                <ProtectedRoute element={<Profile />} />
              </DefaultLayout>
            }
          />
          <Route
            path="/forms/form-elements"
            element={
              <DefaultLayout>
                <PageTitle title="Form Elements | TailAdmin - Tailwind CSS Admin Dashboard Template" />
                <ProtectedRoute element={<FormElements />} />
              </DefaultLayout>
            }
          />
          <Route
            path="/task/:filterDate"
            element={
              <DefaultLayout>
                <PageTitle title="Tasks | TailAdmin - Tailwind CSS Admin Dashboard Template" />
                <ProtectedRoute element={<TaskPage />} />
              </DefaultLayout>
            }
          />
          <Route
            path="/ui/alerts"
            element={
              <DefaultLayout>
                <PageTitle title="Alerts | TailAdmin - Tailwind CSS Admin Dashboard Template" />
                <ProtectedRoute element={<Alerts />} />
              </DefaultLayout>
            }
          />
          <Route
            path="/ui/buttons"
            element={
              <DefaultLayout>
                <PageTitle title="Buttons | TailAdmin - Tailwind CSS Admin Dashboard Template" />
                <ProtectedRoute element={<Buttons />} />
              </DefaultLayout>
            }
          />
          <Route
            path="/auth/signin"
            element={
              <div className="dark:bg-boxdark-2 dark:text-bodydark mx-auto max-w-screen-2xl p-4 md:p-6 2xl:p-10">
                <PageTitle title="Signin | TailAdmin - Tailwind CSS Admin Dashboard Template" />
                <PublicRoute restricted={true} element={<SignIn />} />
              </div>
            }
          />
          <Route
            path="/auth/signup"
            element={
              <div className="dark:bg-boxdark-2 dark:text-bodydark mx-auto max-w-screen-2xl p-4 md:p-6 2xl:p-10">
                <PageTitle title="Signup | TailAdmin - Tailwind CSS Admin Dashboard Template" />
                <PublicRoute restricted={true} element={<SignUp />} />
              </div>
            }
          />
        </Routes>
    </AuthProvider>
  );
}

export default App;
