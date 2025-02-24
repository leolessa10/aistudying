import React, { useState } from "react";
import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

function App() {
  const [tema, setTema] = useState("");
  const [idade, setIdade] = useState("");
  const [videoUrl, setVideoUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGerarVideo = async () => {
    if (!tema.trim() || !idade.trim()) {
      setError("Preencha todos os campos!");
      return;
    }

    setError("");
    setLoading(true);
    setVideoUrl(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/gerar_video`, {
        resumo: tema,
        idade: idade,
      });

      setTimeout(() => {
        setVideoUrl(response.data.video_url);
        setLoading(false);
      }, 2000);
    } catch (err) {
      setError("Erro ao gerar o vídeo.");
      console.error(err);
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h1>Gerador de Vídeos</h1>
      
      <input
        type="text"
        placeholder="Digite o tema"
        value={tema}
        onChange={(e) => {
          setTema(e.target.value);
          setError(""); // Limpa o erro ao digitar
        }}
        style={{ padding: "10px", margin: "10px", width: "80%" }}
      />

      <input
        type="number"
        placeholder="Idade da criança"
        value={idade}
        onChange={(e) => {
          setIdade(e.target.value);
          setError(""); // Limpa o erro ao digitar
        }}
        style={{ padding: "10px", margin: "10px", width: "80%" }}
      />

      <br />
      <button 
        onClick={handleGerarVideo} 
        style={{ padding: "10px 20px" }}
        disabled={loading}
      >
        {loading ? "Gerando..." : "Gerar Vídeo"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {videoUrl ? (
        <div style={{ marginTop: "20px" }}>
          <h3>Vídeo Gerado:</h3>
          <video width="80%" controls>
	      <source src={`${API_BASE_URL}${videoUrl}`} type="video/mp4" />
            Seu navegador não suporta vídeos.
          </video>
        </div>
      ) : loading ? (
        <p>Gerando vídeo... Aguarde alguns segundos.</p>
      ) : null}
    </div>
  );
}

export default App;

