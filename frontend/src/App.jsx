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

import RequirementSummaryPage from "./pages/RequirementSummaryPage";

import ProjectAnalysis from "./pages/ProjectAnalysis";
import FreelancerRecommendationPage
  from "./pages/FreelancerRecommendationPage";
import NegotiationPage from "./pages/NegotiationPage";

import FreelancerDashboard from "./pages/FreelancerDashboard";
import ContractPage from "./pages/ContractPage";

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





        {/* Dashboard */}

        <Route

          path="/dashboard"

          element={
            <Dashboard />
          }

        />

        <Route

          path="/freelancer-dashboard"

          element={
            <FreelancerDashboard />
          }

        />

        <Route

          path="/contract/:projectId"

          element={
            <ContractPage />
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

        <Route
          path="/negotiation/:projectId"
          element={<NegotiationPage />}
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