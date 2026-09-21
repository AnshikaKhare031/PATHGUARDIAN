import React from "react";
import ReportForm from "./components/ReportForm";

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">
          <div className="brand-icon">P</div>
          <div>
            <h1>PathGuardian</h1>
            <p>Smart neighborhood safety</p>
          </div>
        </div>

        <nav className="app-nav">
          <a href="#map">Safety Map</a>
          <a href="#report">Report Incident</a>
        </nav>
      </header>

      <main>
        <section id="map" className="hero-section">
          <div className="hero-content">
            <span className="eyebrow">COMMUNITY SAFETY</span>
            <h2>Know your surroundings.<br />Choose safer paths.</h2>
            <p>
              Explore neighborhood safety conditions and help your community
              by reporting incidents and unsafe areas.
            </p>

            <div className="hero-actions">
              <a href="#map-area" className="primary-action">
                Explore Safety Map
              </a>
              <a href="#report" className="secondary-action">
                Report an Incident
              </a>
            </div>
          </div>

          <div className="safety-summary">
            <div className="summary-header">
              <span>Area Safety Overview</span>
              <span className="status-dot">Live</span>
            </div>

            <div className="safety-score">
              <strong>72</strong>
              <span>/ 100</span>
            </div>

            <p>Overall safety score</p>

            <div className="score-bar">
              <div className="score-progress"></div>
            </div>

            <div className="summary-footer">
              <span>Community reports</span>
              <strong>Active</strong>
            </div>
          </div>
        </section>

        <section id="map-area" className="map-section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">LIVE VIEW</span>
              <h2>Safety Map</h2>
              <p>
                Visualize safety conditions across your neighborhood.
              </p>
            </div>

            <div className="map-legend">
              <span><i className="safe-dot"></i> Safer</span>
              <span><i className="moderate-dot"></i> Moderate</span>
              <span><i className="risk-dot"></i> Higher risk</span>
            </div>
          </div>

          <div className="map-box">
            <div className="map-road road-one"></div>
            <div className="map-road road-two"></div>
            <div className="map-road road-three"></div>

            <div className="map-zone zone-one"></div>
            <div className="map-zone zone-two"></div>
            <div className="map-zone zone-three"></div>

            <div className="map-pin pin-one">●</div>
            <div className="map-pin pin-two">●</div>
            <div className="map-pin pin-three">●</div>

            <div className="map-center-card">
              <strong>Safety map</strong>
              <span>Map integration ready</span>
            </div>
          </div>
        </section>

        <section className="features-section">
          <div className="feature-card">
            <div className="feature-icon">01</div>
            <h3>Safety Reports</h3>
            <p>
              Report incidents, poor lighting, suspicious activity and unsafe
              areas.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">02</div>
            <h3>Safety Score</h3>
            <p>
              Safety conditions are represented through an easy-to-understand
              score.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">03</div>
            <h3>Safer Routes</h3>
            <p>
              Use safety information to identify routes with better conditions.
            </p>
          </div>
        </section>

        <section id="report">
          <ReportForm />
        </section>
      </main>

      <footer className="app-footer">
        <strong>PathGuardian</strong>
        <span>Building safer neighborhoods through community data.</span>
      </footer>
    </div>
  );
}

export default App;