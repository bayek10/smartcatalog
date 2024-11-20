import { SearchForm } from '../components/SearchForm'

function App() {
  return (
    <div className="App">
      <header className="app-header">
        <h1>Smart Catalog</h1>
        <p className="app-description">
          Transform your PDF catalogs into searchable product data in minutes
        </p>
      </header>
      <SearchForm />
    </div>
  )
}

export default App
