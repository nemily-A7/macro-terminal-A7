export default function SkeletonCard() {
  return (
    <div className="flex flex-col gap-3 p-4 bg-card rounded-xl border border-subtle">
      <div className="flex justify-between">
        <div className="skeleton h-2.5 w-20 rounded" />
        <div className="skeleton h-2.5 w-8 rounded" />
      </div>
      <div className="skeleton h-7 w-24 rounded" />
      <div className="skeleton h-2 w-14 rounded" />
      <div className="skeleton h-10 rounded" />
    </div>
  );
}
