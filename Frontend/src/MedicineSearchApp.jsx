import React, { useState } from 'react';
import { Search, ExternalLink, Pill, Loader2, AlertCircle } from 'lucide-react';

function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

const MedicineSearchApp = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setError('Merci de saisir un terme afin de lancer la recherche.');
      return;
    }

    setIsSearching(true);
    setShowResults(true);
    setError('');

    try {
      const response = await fetch('http://127.0.0.1:5000/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query: searchQuery,
          top_k: 5 
        }),
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la recherche');
      }

      const data = await response.json();
      
      if (data.message) {
        setResults([]);
        setError('');
      } else {
        setResults(data.results || []);
        setError('');
      }
    } catch (err) {
      setError('Erreur de connexion au serveur. Assurez-vous que le backend est démarré.');
      console.error(err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const highlightText = (text, query) => {
    if (!query.trim() || !text) return text;
    const words = query.toLowerCase().split(' ').filter(w => w.trim());
    let highlighted = text;
  
    words.forEach(word => {
      try {
        const safeWord = escapeRegExp(word);
        const regex = new RegExp(`(${safeWord})`, 'gi');
        highlighted = highlighted.replace(regex, '<mark class="bg-red-500 text-white px-1 rounded">$1</mark>');
      } catch (e) {
        console.warn('Regex error for word:', word, e);
      }
    });
  
    return <span dangerouslySetInnerHTML={{ __html: highlighted }} />;
  };

  const getHostname = (url) => {
    if (!url || url === '#') return 'medicaments.gouv.fr';
    try {
      return new URL(url).hostname;
    } catch {
      return 'medicaments.gouv.fr';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800">
      {/* Header */}
      <header className="bg-gray-800/50 backdrop-blur-sm shadow-lg border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-3">
          <Pill className="w-8 h-8 text-red-500" />
          <h1 className="text-2xl font-bold text-white">MediSearch</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Logo centré avant recherche */}
        {!showResults && (
          <div className="text-center mb-12 mt-20">
            <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-red-500 to-red-600 rounded-full mb-6 shadow-2xl shadow-red-500/30">
              <Pill className="w-12 h-12 text-white" />
            </div>
            <h2 className="text-5xl font-bold text-white mb-2">MediSearch</h2>
            <p className="text-xl text-gray-300">Recherchez parmi des milliers de médicaments</p>
          </div>
        )}

        {/* Barre de recherche */}
        <div className={`${showResults ? 'mb-8' : 'mb-4'}`}>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="w-5 h-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Rechercher un médicament (ex: doliprane, antibiotique, ibuprofène...)"
              className="w-full pl-12 pr-4 py-4 text-lg bg-gray-800/90 border-2 border-gray-700 rounded-full shadow-lg focus:outline-none focus:border-red-500 focus:ring-2 focus:ring-red-500/50 transition-all text-white placeholder-gray-400"
            />
            <button
              onClick={handleSearch}
              disabled={isSearching}
              className="absolute right-2 top-1/2 -translate-y-1/2 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white px-6 py-2 rounded-full font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
            >
              {isSearching ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                'Rechercher'
              )}
            </button>
          </div>
        </div>

        {/* Message d'erreur */}
        {error && (
          <div className="bg-red-900/30 border border-red-700/50 rounded-lg p-4 mb-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
            <div>
             <p className="text-red-300 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Nombre de resultat */}
        {showResults && results.length > 0 && !isSearching && (
          <div className="text-sm text-gray-400 mb-4">
            Environ {results.length} résultat{results.length > 1 ? 's' : ''}
          </div>
        )}

        {/* Loading */}
        {isSearching && (
          <div className="text-center py-12">
            <Loader2 className="w-12 h-12 text-red-500 animate-spin mx-auto mb-4" />
            <p className="text-gray-300">Recherche en cours...</p>
          </div>
        )}

        {/* Résultats de recherche */}
        {showResults && !isSearching && results.length > 0 && (
          <div className="space-y-6">
            {results.map((result, index) => (
              <div
                key={result.doc_id || index}
                className="bg-gray-800/70 backdrop-blur-sm rounded-lg shadow-xl hover:shadow-2xl hover:shadow-red-500/10 transition-all p-6 border border-gray-700 hover:border-red-500/50"
              >
                <div className="flex gap-4">
                  {/* Image du médicament */}
                  <div className="flex-shrink-0">
                    <img
                      src={result.image_url || `https://placehold.co/80x80/ef4444/white?text=${result.nom ? result.nom.charAt(0) : 'M'}`}
                      alt={result.nom || 'Médicament'}
                      className="w-20 h-20 rounded-lg object-cover border border-gray-600"
                    />
                  </div>

                  {/* Contenu */}
                  <div className="flex-1 min-w-0">
                    {/* Titre avec lien */}
                    <a
                      href={result.url && result.url !== '#' ? result.url : undefined}
                      target={result.url && result.url !== '#' ? "_blank" : undefined}
                      rel={result.url && result.url !== '#' ? "noopener noreferrer" : undefined}
                      className={`group ${result.url && result.url !== '#' ? 'cursor-pointer' : 'cursor-default'}`}
                    >
                      <h3 className={`text-xl font-semibold mb-1 flex items-start gap-2 ${result.url && result.url !== '#' ? 'text-red-400 hover:text-red-300 group-hover:underline' : 'text-gray-200'}`}>
                        {result.nom ? highlightText(result.nom, searchQuery) : 'Médicament'}
                        {result.url && result.url !== '#' && (
                          <ExternalLink className="w-4 h-4 mt-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                        )}
                      </h3>
                    </a>

                    {/* URL */}
                    <div className="text-sm text-green-400 mb-2">
                      {getHostname(result.url)}
                    </div>

                    {/* Score de pertinence */}
                    {result.score && (
                      <div className="inline-block bg-red-500/20 text-red-300 text-xs font-semibold px-2 py-1 rounded mb-2 border border-red-500/30">
                        Score: {(result.score * 100).toFixed(1)}%
                      </div>
                    )}

                    {/* Snippet */}
                    <p className="text-gray-300 text-sm leading-relaxed">
                      {result.snippet ? highlightText(result.snippet, searchQuery) : 'Aucune description disponible.'}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Aucun résultat après recherche */}
        {showResults && results.length === 0 && (
          <div className="text-center py-12">
            <AlertCircle className="w-16 h-16 text-gray-500 mx-auto mb-4" />
            <p className="text-xl text-gray-200">Aucun médicament trouvé</p>
            <p className="text-gray-400 mt-2">
              Le médicament "<span className="font-semibold text-red-400">{searchQuery}</span>" n'existe pas dans notre base de données.
            </p>
            <p className="text-gray-400 mt-3">
              💡 Suggestions :
            </p>
            <ul className="text-gray-400 mt-2 space-y-1">
              <li>• Vérifiez l'orthographe</li>
              <li>• Essayez un nom commercial (Doliprane, Advil...)</li>
              <li>• Essayez une substance active (paracétamol, ibuprofène...)</li>
              <li>• Essayez un symptôme (douleur, fièvre, toux...)</li>
            </ul>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 py-8 text-center text-gray-400 text-sm">
        <p>Système de Recherche d'Information - Projet SRI</p>
        <p className="mt-1">Données issues de la base publique des médicaments</p>
      </footer>
    </div>
  );
};

export default MedicineSearchApp;