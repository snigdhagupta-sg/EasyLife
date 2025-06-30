import UploadForm from "../components/UploadForm";
import ResultCard from "../components/ResultCard";
import { useState } from "react";

export default function Home() {
  const [result, setResult] = useState(null);
  return (
    <div className="container mx-auto py-10">
      <UploadForm onResult={setResult} />
      {result && <ResultCard data={result} />}
    </div>
  );
}
