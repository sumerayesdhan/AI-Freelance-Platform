import {
    BrowserRouter,
    Routes,
    Route,
    Navigate
} from "react-router-dom";


import Register from "./pages/Register";
import Login from "./pages/Login";
import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";
import ClientStartPage from "./pages/ClientStartPage";
import ProcessingProjectsPage from "./pages/ProcessingProjectsPage";


import RequirementAssistance
    from "./pages/RequirementAssistance";


import FreelancerLogin
    from "./pages/FreelancerLogin";


import RequirementSummaryPage
    from "./pages/RequirementSummaryPage";


import ProjectAnalysis
    from "./pages/ProjectAnalysis";


import FreelancerRecommendationPage
    from "./pages/FreelancerRecommendationPage";


import FreelancerRegister
    from "./pages/FreelancerRegister";


import FreelancerDashboard
    from "./pages/FreelancerDashboard";


import NegotiationPage
    from "./pages/NegotiationPage";


import ContractWorkspace
    from "./pages/ContractWorkspace";

import ContractGenerationPage
    from "./pages/ContractGenerationPage";

import TimelineGenerationPage
    from "./pages/TimelineGenerationPage";


function App() {

    return (

        <BrowserRouter>

            <Routes>


                {/* =================================================
                    DEFAULT
                ================================================= */}

                <Route

                    path="/"

                    element={
                        <Landing />
                    }

                />


                {/* =================================================
                    CLIENT AUTHENTICATION
                ================================================= */}

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


                {/* =================================================
                    FREELANCER AUTHENTICATION
                ================================================= */}

                <Route

                    path="/freelancer-register"

                    element={
                        <FreelancerRegister />
                    }

                />


                <Route

                    path="/freelancer-login"

                    element={
                        <FreelancerLogin />
                    }

                />


                {/* =================================================
                    FREELANCER DASHBOARD
                ================================================= */}

                <Route

                    path="/freelancer-dashboard/:freelancerId"

                    element={
                        <FreelancerDashboard />
                    }

                />


                {/* =================================================
                    CLIENT DASHBOARD
                ================================================= */}

                <Route

                    path="/dashboard"

                    element={
                        <Dashboard />
                    }

                />


                <Route
                    path="/client-start"
                    element={<ClientStartPage />}
                />


                <Route
                    path="/processing-projects"
                    element={<ProcessingProjectsPage />}
                />


                {/* =================================================
                    REQUIREMENT GATHERING
                ================================================= */}

                <Route

                    path="/requirement-assistance/:projectId"

                    element={
                        <RequirementAssistance />
                    }

                />


                {/* =================================================
                    REQUIREMENT RESULT
                ================================================= */}

                <Route

                    path="/requirement-summary/:projectId"

                    element={
                        <RequirementSummaryPage />
                    }

                />


                {/* =================================================
                    PROJECT ANALYSIS
                ================================================= */}

                <Route

                    path="/project/:projectId/analysis"

                    element={
                        <ProjectAnalysis />
                    }

                />


                {/* =================================================
                    FREELANCER RECOMMENDATION
                ================================================= */}

                <Route

                    path="/freelancers/:projectId"

                    element={
                        <FreelancerRecommendationPage />
                    }

                />


                {/* =================================================
                    NEGOTIATION
                ================================================= */}

                <Route

                    path="/negotiation/:requestId"

                    element={
                        <NegotiationPage />
                    }

                />


                <Route

                    path="/contract-workspace/:requestId"

                    element={
                        <ContractWorkspace />
                    }

                />


                <Route
                    path="/contract/:requestId"
                    element={<ContractGenerationPage />}
                />


                <Route
                    path="/timeline/:requestId"
                    element={<TimelineGenerationPage />}
                />


                {/* =================================================
                    UNKNOWN URL
                ================================================= */}

                <Route

                    path="*"

                    element={
                        <Landing />
                    }

                />

            </Routes>

        </BrowserRouter>

    );

}


export default App;