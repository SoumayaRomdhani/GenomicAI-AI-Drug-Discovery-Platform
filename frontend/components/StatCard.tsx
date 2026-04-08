type Props = {
  value: string;
  label: string;
};

export default function StatCard({ value, label }: Props) {
  return (
    <div className="stat-card">
      <div className="stat-value">{value}</div>
      <div className="muted">{label}</div>
    </div>
  );
}
