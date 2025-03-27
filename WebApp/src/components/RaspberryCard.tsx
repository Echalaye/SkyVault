import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { fetchRaspberryData } from "@/lib/firebase";
import type { RaspberryData } from "@/types";
import {
  DropletIcon,
  FlameIcon,
  RefreshCwIcon,
  Clock,
  PauseIcon,
  PlayIcon,
} from "lucide-react";
import { useTheme } from "./theme-provider";

export function RaspberryCard() {
  const [raspberryData, setRaspberryData] = useState<RaspberryData | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [nextRefresh, setNextRefresh] = useState(5);
  const { theme } = useTheme();
  const isDarkMode =
    theme === "dark" ||
    (theme === "system" &&
      window.matchMedia("(prefers-color-scheme: dark)").matches);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchRaspberryData();
      setRaspberryData(data);
      // Réinitialiser le compteur après chaque rafraîchissement
      setNextRefresh(5);
    } catch (err) {
      setError("Erreur lors de la récupération des données");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Charger les données au premier rendu
  useEffect(() => {
    loadData();
  }, []);

  // Configuration du rafraîchissement automatique
  useEffect(() => {
    let intervalId: number | undefined;
    let countdownId: number | undefined;

    if (autoRefresh) {
      // Intervalle principal pour charger les données toutes les 5 secondes
      intervalId = window.setInterval(() => {
        loadData();
      }, 5000);

      // Intervalle pour décrémenter le compteur de secondes
      countdownId = window.setInterval(() => {
        setNextRefresh((prev) => (prev > 0 ? prev - 1 : 5));
      }, 1000);
    }

    // Nettoyer les intervalles quand le composant est démonté ou quand autoRefresh change
    return () => {
      if (intervalId) window.clearInterval(intervalId);
      if (countdownId) window.clearInterval(countdownId);
    };
  }, [autoRefresh]);

  // Formater une date depuis un timestamp
  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleString("fr-FR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh((prev) => !prev);
  };

  return (
    <Card
      className={`w-full max-w-md mx-auto shadow-lg hover:shadow-xl transition-shadow ${
        isDarkMode ? "bg-zinc-900 border-zinc-800" : "bg-white"
      }`}
    >
      <CardHeader
        className={`${
          isDarkMode
            ? "bg-gradient-to-r from-blue-950 via-indigo-800 to-blue-950"
            : "bg-gradient-to-r from-blue-100 via-indigo-100 to-blue-200"
        }`}
      >
        <div className="flex justify-between items-center mt-2">
          <CardTitle
            className={`text-xl font-bold ${
              isDarkMode ? "text-white" : "text-zinc-900"
            }`}
          >
            Capteurs Raspberry Pi
          </CardTitle>
          <div className="flex items-center gap-1">
            <Clock
              size={16}
              className={isDarkMode ? "text-zinc-300" : "text-zinc-700"}
            />
            <span
              className={`text-sm ${
                isDarkMode ? "text-zinc-300" : "text-zinc-700"
              }`}
            >
              {autoRefresh ? `${nextRefresh}s` : "Pause"}
            </span>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-6 min-h-[180px] relative">
        {error ? (
          <div className="text-red-500 text-center py-4">{error}</div>
        ) : loading && !raspberryData ? (
          <div
            className={`absolute inset-0 flex items-center justify-center ${
              isDarkMode ? "text-zinc-300" : "text-zinc-800"
            }`}
          >
            <div className="flex flex-col items-center">
              <RefreshCwIcon
                className={`animate-spin h-8 w-8 mb-2 ${
                  isDarkMode ? "text-blue-400" : "text-blue-600"
                }`}
              />
              <span>Chargement...</span>
            </div>
          </div>
        ) : loading && raspberryData ? (
          // Pendant le chargement, continuer à afficher les anciennes données avec un indicateur de chargement
          <div className="space-y-4">
            <div
              className={`flex items-center justify-between p-3 rounded-lg ${
                isDarkMode ? "bg-blue-900" : "bg-blue-50"
              } relative overflow-hidden`}
            >
              <div className="flex items-center">
                <DropletIcon
                  className={`mr-2 ${
                    isDarkMode ? "text-blue-400" : "text-blue-500"
                  }`}
                  size={24}
                />
                <span
                  className={`font-medium ${
                    isDarkMode ? "text-zinc-50" : "text-zinc-900"
                  }`}
                >
                  Humidité
                </span>
              </div>
              <div
                className={`text-lg font-bold ${
                  isDarkMode ? "text-zinc-50" : "text-zinc-900"
                }`}
              >
                {raspberryData.humidity.value}%
              </div>
              <div
                className={`absolute inset-0 flex items-center justify-center ${
                  isDarkMode ? "bg-zinc-900/40" : "bg-white/40"
                }`}
              >
                <RefreshCwIcon
                  className={`animate-spin h-6 w-6 ${
                    isDarkMode ? "text-blue-400" : "text-blue-600"
                  }`}
                />
              </div>
            </div>

            {raspberryData.gas && (
              <div
                className={`flex items-center justify-between p-3 rounded-lg ${
                  isDarkMode ? "bg-orange-900" : "bg-orange-50"
                } relative overflow-hidden`}
              >
                <div className="flex items-center">
                  <FlameIcon
                    className={`mr-2 ${
                      isDarkMode ? "text-orange-400" : "text-orange-500"
                    }`}
                    size={24}
                  />
                  <span
                    className={`font-medium ${
                      isDarkMode ? "text-zinc-50" : "text-zinc-900"
                    }`}
                  >
                    Gaz
                  </span>
                </div>
                <div
                  className={`text-lg font-bold ${
                    isDarkMode ? "text-zinc-50" : "text-zinc-900"
                  }`}
                >
                  {raspberryData.gas.value} ppm
                </div>
                <div
                  className={`absolute inset-0 flex items-center justify-center ${
                    isDarkMode ? "bg-zinc-900/40" : "bg-white/40"
                  }`}
                >
                  <RefreshCwIcon
                    className={`animate-spin h-6 w-6 ${
                      isDarkMode ? "text-orange-400" : "text-orange-600"
                    }`}
                  />
                </div>
              </div>
            )}

            <div
              className={`text-xs text-right mt-2 ${
                isDarkMode ? "text-gray-400" : "text-gray-600"
              }`}
            >
              Dernière mise à jour:{" "}
              {formatDate(raspberryData.humidity.last_updated)}
            </div>
          </div>
        ) : raspberryData ? (
          <div className="space-y-4">
            <div
              className={`flex items-center justify-between p-3 rounded-lg ${
                isDarkMode ? "bg-blue-900" : "bg-blue-50"
              }`}
            >
              <div className="flex items-center">
                <DropletIcon
                  className={`mr-2 ${
                    isDarkMode ? "text-blue-400" : "text-blue-500"
                  }`}
                  size={24}
                />
                <span
                  className={`font-medium ${
                    isDarkMode ? "text-zinc-50" : "text-zinc-900"
                  }`}
                >
                  Humidité
                </span>
              </div>
              <div
                className={`text-lg font-bold ${
                  isDarkMode ? "text-zinc-50" : "text-zinc-900"
                }`}
              >
                {raspberryData.humidity.value}%
              </div>
            </div>

            {raspberryData.gas && (
              <div
                className={`flex items-center justify-between p-3 rounded-lg ${
                  isDarkMode ? "bg-orange-900" : "bg-orange-50"
                }`}
              >
                <div className="flex items-center">
                  <FlameIcon
                    className={`mr-2 ${
                      isDarkMode ? "text-orange-400" : "text-orange-500"
                    }`}
                    size={24}
                  />
                  <span
                    className={`font-medium ${
                      isDarkMode ? "text-zinc-50" : "text-zinc-900"
                    }`}
                  >
                    Gaz
                  </span>
                </div>
                <div
                  className={`text-lg font-bold ${
                    isDarkMode ? "text-zinc-50" : "text-zinc-900"
                  }`}
                >
                  {raspberryData.gas.value} ppm
                </div>
              </div>
            )}

            <div
              className={`text-xs text-right mt-2 ${
                isDarkMode ? "text-gray-400" : "text-gray-600"
              }`}
            >
              Dernière mise à jour:{" "}
              {formatDate(raspberryData.humidity.last_updated)}
            </div>
          </div>
        ) : (
          <div
            className={`flex items-center justify-center h-full ${
              isDarkMode ? "text-zinc-300" : "text-zinc-800"
            }`}
          >
            Aucune donnée disponible
          </div>
        )}
      </CardContent>
      <CardFooter
        className={`flex justify-between items-center border-t pt-4 ${
          isDarkMode ? "border-zinc-800" : ""
        }`}
      >
        <Button
          variant="outline"
          size="icon"
          onClick={toggleAutoRefresh}
          className="w-10 h-10"
          title={
            autoRefresh
              ? "Désactiver l'actualisation automatique"
              : "Activer l'actualisation automatique"
          }
        >
          {autoRefresh ? (
            <PauseIcon className="h-4 w-4" />
          ) : (
            <PlayIcon className="h-4 w-4" />
          )}
        </Button>

        <Button onClick={loadData} disabled={loading} className="flex-1 ml-2">
          <RefreshCwIcon
            className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`}
          />
          Rafraîchir
        </Button>
      </CardFooter>
    </Card>
  );
}
