export default function ResultCard({ data }) {
  return (
    <div className="bg-white p-6 shadow rounded mt-4">
      <h2 className="text-lg font-semibold mb-2">Extracted Data</h2>
      <dl>
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="flex justify-between py-1">
            <dt className="font-medium">{key}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
