import {
  BrowserRouter,
  Routes,
  Route,
  Navigate
} from "react-router-dom";


import Register from "./pages/Register";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";

import RequirementAssistance from "./pages/RequirementAssistance";
import FreelancerLogin from "./pages/FreelancerLogin";
import RequirementSummaryPage from "./pages/RequirementSummaryPage";

import ProjectAnalysis from "./pages/ProjectAnalysis";
import FreelancerRecommendationPage
  from "./pages/FreelancerRecommendationPage";

import FreelancerRegister
  from "./pages/FreelancerRegister";

import FreelancerDashboard
  from "./pages/FreelancerDashboard";

function App() {


  return (

    <BrowserRouter>


      <Routes>


        {/* Default */}

        <Route

          path="/"

          element={
            <Navigate to="/register" />
          }

        />



        {/* Authentication */}

        <Route

          path="/register"

          element={
            <Register />
          }

        />



        <Route

          path="/login"

          element={
            <Login />
          }

        />


        {/* Freelancer Authentication */}

        <Route

          path="/freelancer-register"

          element={
            <FreelancerRegister />
          }

        />


        {/* Freelancer Dashboard */}

        <Route

          path="/freelancer-dashboard/:freelancerId"

          element={
            <FreelancerDashboard />
          }

        />
        <Route
          path="/freelancer-login"
          element={<FreelancerLogin />}
        />

        {/* Dashboard */}

        <Route

          path="/dashboard"

          element={
            <Dashboard />
          }

        />





        {/* Requirement Gathering */}

        <Route

          path="/requirement-assistance/:projectId"

          element={
            <RequirementAssistance />
          }

        />





        {/* Requirement Result */}

        <Route

          path="/requirement-summary/:projectId"

          element={
            <RequirementSummaryPage />
          }

        />





        {/* Final Analysis */}

        <Route

          path="/project/:projectId/analysis"

          element={
            <ProjectAnalysis />
          }

        />


        <Route

          path="/freelancers/:projectId"

          element={
            <FreelancerRecommendationPage />
          }

        />


        {/* Unknown URLs */}

        <Route

          path="*"

          element={
            <Navigate to="/register" />
          }

        />


      </Routes>


    </BrowserRouter>

  );

}


export default App;