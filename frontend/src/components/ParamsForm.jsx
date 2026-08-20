/** 由策略参数 schema 生成的表单。value/onChange 为受控对象 {paramName: value}。 */
export default function ParamsForm({ params, value, onChange }) {
  if (!params || !params.length) return null

  const set = (name, v) => onChange({ ...value, [name]: v })

  return (
    <div className="field-grid">
      {params.map((p) => (
        <label className="field" key={p.name}>
          <span className="field-label" title={p.description || ''}>
            {p.label}
            {p.description ? <em className="hint"> ?</em> : null}
          </span>
          <input
            type="number"
            step={p.step ?? (p.ptype === 'int' ? 1 : 0.01)}
            min={p.min}
            max={p.max}
            value={value[p.name] ?? p.default ?? ''}
            onChange={(e) => {
              const v = e.target.value
              set(p.name, v === '' ? '' : p.ptype === 'int' ? parseInt(v, 10) : parseFloat(v))
            }}
          />
        </label>
      ))}
    </div>
  )
}
