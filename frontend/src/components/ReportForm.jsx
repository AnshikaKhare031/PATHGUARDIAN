import React, { useState } from "react";
import "./ReportForm.css";

const ReportForm = () => {
  const [reportType, setReportType] = useState("");
  const [description, setDescription] = useState("");
  const [location, setLocation] = useState("");
  const [severity, setSeverity] = useState("");
  const [incidentTime, setIncidentTime] = useState("");
  const [anonymous, setAnonymous] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (!reportType) {
      setError("Please select a safety concern.");
      return;
    }

    if (!description.trim()) {
      setError("Please describe what happened.");
      return;
    }

    if (!location.trim()) {
      setError("Please enter the location.");
      return;
    }

    if (!severity) {
      setError("Please select the severity.");
      return;
    }

    if (!incidentTime) {
      setError("Please select when the incident happened.");
      return;
    }

    const safetyRating = {
      low: 1,
      medium: 3,
      high: 5,
    };

    if (!navigator.geolocation) {
      setError("Location services are not supported by this browser.");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;

        const comment = `
Concern: ${reportType}
Description: ${description}
Location: ${location}
Severity: ${severity}
Incident Time: ${incidentTime}
Anonymous: ${anonymous ? "Yes" : "No"}
        `.trim();

        const reportData = {
          lat: latitude,
          lng: longitude,
          safety_rating: safetyRating[severity],
          comment: comment,
        };

        try {
          const response = await fetch(
            "http://127.0.0.1:8000/api/reports",
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify(reportData),
            }
          );

          if (!response.ok) {
            throw new Error("Failed to submit report.");
          }

          const data = await response.json();

          console.log("Report submitted:", data);

          setSuccess("Report submitted successfully!");

          setReportType("");
          setDescription("");
          setLocation("");
          setSeverity("");
          setIncidentTime("");
          setAnonymous(false);
        } catch (err) {
          console.error(err);
          setError("Failed to submit report. Please try again.");
        }
      },
      () => {
        setError(
          "Unable to access your location. Please allow location permission."
        );
      }
    );
  };

  return (
    <div className="report-container">
      <div className="report-header">
        <h2>PathGuardian</h2>
        <p>
          Help make your neighborhood safer by reporting incidents and unsafe
          conditions.
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <label>What happened?</label>

        <select
          required
          value={reportType}
          onChange={(e) => setReportType(e.target.value)}
        >
          <option value="">Select a concern</option>
          <option value="poor_lighting">Poor Street Lighting</option>
          <option value="harassment">Harassment</option>
          <option value="suspicious_activity">Suspicious Activity</option>
          <option value="unsafe_area">Unsafe Area</option>
          <option value="other">Other</option>
        </select>

        <label>Description</label>

        <textarea
          required
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe what happened..."
        />

        <label>Location</label>

        <input
          type="text"
          required
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="Enter the location"
        />

        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={anonymous}
            onChange={(e) => setAnonymous(e.target.checked)}
          />
          Submit anonymously
        </label>

        <label>Severity</label>

        <select
          required
          value={severity}
          onChange={(e) => setSeverity(e.target.value)}
        >
          <option value="">Select severity</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>

        <label>When did it happen?</label>
        <p className="location-note">
  Your current location helps us accurately place this report on the safety map.
</p>

        <input
          type="datetime-local"
          required
          value={incidentTime}
          onChange={(e) => setIncidentTime(e.target.value)}
        />

        {error && <p className="error">{error}</p>}

        {success && <p className="success">{success}</p>}

        <button type="submit">Submit Safety Report</button>
      </form>
    </div>
  );
};

export default ReportForm;