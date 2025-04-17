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
  AlertTriangleIcon,
} from "lucide-react";
import { useTheme } from "./theme-provider";

// Types de niveaux pour les capteurs
type HumidityLevel = "low" | "moderate" | "comfortable" | "high" | "veryHigh";
type GasLevel = "low" | "moderate" | "high";

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

  // Déterminer le niveau d'humidité
  const getHumidityLevel = (humidity: number): HumidityLevel => {
    if (humidity < 30) return "low";
    if (humidity < 50) return "moderate";
    if (humidity < 60) return "comfortable";
    if (humidity < 80) return "high";
    return "veryHigh";
  };

  // Déterminer le niveau de gaz
  const getGasLevel = (gas: number): GasLevel => {
    if (gas < 50) return "low";
    if (gas < 200) return "moderate";
    return "high";
  };

  // Obtenir le texte descriptif pour le niveau d'humidité
  const getHumidityText = (level: HumidityLevel): string => {
    switch (level) {
      case "low":
        return "Humidité faible";
      case "moderate":
        return "Humidité modérée";
      case "comfortable":
        return "Humidité confortable";
      case "high":
        return "Humidité élevée";
      case "veryHigh":
        return "Humidité très élevée";
    }
  };

  // Obtenir le texte descriptif pour le niveau de gaz
  const getGasText = (level: GasLevel): string => {
    switch (level) {
      case "low":
        return "Concentration faible";
      case "moderate":
        return "Concentration modérée";
      case "high":
        return "Concentration élevée";
    }
  };

  // Obtenir les couleurs pour le niveau d'humidité
  const getHumidityColors = (level: HumidityLevel) => {
    switch (level) {
      case "low":
        return {
          bg: isDarkMode ? "bg-blue-900/30" : "bg-blue-50",
          text: isDarkMode ? "text-blue-300" : "text-blue-700",
          level: isDarkMode ? "text-yellow-400" : "text-yellow-600",
        };
      case "moderate":
        return {
          bg: isDarkMode ? "bg-blue-900/40" : "bg-blue-100",
          text: isDarkMode ? "text-blue-300" : "text-blue-700",
          level: isDarkMode ? "text-green-400" : "text-green-600",
        };
      case "comfortable":
        return {
          bg: isDarkMode ? "bg-blue-900/50" : "bg-blue-100",
          text: isDarkMode ? "text-blue-300" : "text-blue-700",
          level: isDarkMode ? "text-green-400" : "text-green-600",
        };
      case "high":
        return {
          bg: isDarkMode ? "bg-blue-900/60" : "bg-blue-200",
          text: isDarkMode ? "text-blue-300" : "text-blue-700",
          level: isDarkMode ? "text-orange-400" : "text-orange-600",
        };
      case "veryHigh":
        return {
          bg: isDarkMode ? "bg-blue-900/70" : "bg-blue-200",
          text: isDarkMode ? "text-blue-300" : "text-blue-700",
          level: isDarkMode ? "text-red-400" : "text-red-600",
        };
    }
  };

  // Obtenir les couleurs pour le niveau de gaz
  const getGasColors = (level: GasLevel) => {
    switch (level) {
      case "low":
        return {
          bg: isDarkMode ? "bg-orange-900/30" : "bg-orange-50",
          text: isDarkMode ? "text-orange-300" : "text-orange-700",
          level: isDarkMode ? "text-green-400" : "text-green-600",
        };
      case "moderate":
        return {
          bg: isDarkMode ? "bg-orange-900/50" : "bg-orange-100",
          text: isDarkMode ? "text-orange-300" : "text-orange-700",
          level: isDarkMode ? "text-yellow-400" : "text-yellow-600",
        };
      case "high":
        return {
          bg: isDarkMode ? "bg-orange-900/70" : "bg-orange-200",
          text: isDarkMode ? "text-orange-300" : "text-orange-700",
          level: isDarkMode ? "text-red-400" : "text-red-600",
        };
    }
  };

  // Vérifier si un seuil d'alerte est dépassé
  const isHumidityAlertThreshold = (humidity: number): boolean => {
    return humidity > 60;
  };

  const isGasAlertThreshold = (gas: number): boolean => {
    return gas > 200;
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
            {/* Humidité - avec chargement */}
            <div
              className={`rounded-lg relative overflow-hidden ${
                getHumidityColors(
                  getHumidityLevel(parseInt(raspberryData.humidity.value))
                ).bg
              }`}
            >
              <div className="p-3">
                <div className="flex items-center justify-between mb-1">
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

                <div className="flex justify-between items-center">
                  <span
                    className={
                      getHumidityColors(
                        getHumidityLevel(parseInt(raspberryData.humidity.value))
                      ).level
                    }
                  >
                    {getHumidityText(
                      getHumidityLevel(parseInt(raspberryData.humidity.value))
                    )}
                  </span>

                  {isHumidityAlertThreshold(
                    parseInt(raspberryData.humidity.value)
                  ) && (
                    <div
                      className={`flex items-center ${
                        isDarkMode ? "text-amber-400" : "text-amber-600"
                      }`}
                    >
                      <AlertTriangleIcon size={16} className="mr-1" />
                      <span className="text-sm">Humidité trop élevée</span>
                    </div>
                  )}
                </div>
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

            {/* Gaz - avec chargement */}
            {raspberryData.gas && (
              <div
                className={`rounded-lg relative overflow-hidden ${
                  getGasColors(getGasLevel(parseInt(raspberryData.gas.value)))
                    .bg
                }`}
              >
                <div className="p-3">
                  <div className="flex items-center justify-between mb-1">
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

                  <div className="flex justify-between items-center">
                    <span
                      className={
                        getGasColors(
                          getGasLevel(parseInt(raspberryData.gas.value))
                        ).level
                      }
                    >
                      {getGasText(
                        getGasLevel(parseInt(raspberryData.gas.value))
                      )}
                    </span>

                    {isGasAlertThreshold(parseInt(raspberryData.gas.value)) && (
                      <div
                        className={`flex items-center ${
                          isDarkMode ? "text-amber-400" : "text-amber-600"
                        }`}
                      >
                        <AlertTriangleIcon size={16} className="mr-1" />
                        <span className="text-sm">
                          Concentration trop élevée
                        </span>
                      </div>
                    )}
                  </div>
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
            {/* Humidité - sans chargement */}
            <div
              className={`rounded-lg overflow-hidden ${
                getHumidityColors(
                  getHumidityLevel(parseInt(raspberryData.humidity.value))
                ).bg
              }`}
            >
              <div className="p-3">
                <div className="flex items-center justify-between mb-1">
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

                <div className="flex justify-between items-center">
                  <span
                    className={
                      getHumidityColors(
                        getHumidityLevel(parseInt(raspberryData.humidity.value))
                      ).level
                    }
                  >
                    {getHumidityText(
                      getHumidityLevel(parseInt(raspberryData.humidity.value))
                    )}
                  </span>

                  {isHumidityAlertThreshold(
                    parseInt(raspberryData.humidity.value)
                  ) && (
                    <div
                      className={`flex items-center ${
                        isDarkMode ? "text-amber-400" : "text-amber-600"
                      }`}
                    >
                      <AlertTriangleIcon size={16} className="mr-1" />
                      <span className="text-sm">Humidité trop élevée</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Gaz - sans chargement */}
            {raspberryData.gas && (
              <div
                className={`rounded-lg overflow-hidden ${
                  getGasColors(getGasLevel(parseInt(raspberryData.gas.value)))
                    .bg
                }`}
              >
                <div className="p-3">
                  <div className="flex items-center justify-between mb-1">
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

                  <div className="flex justify-between items-center">
                    <span
                      className={
                        getGasColors(
                          getGasLevel(parseInt(raspberryData.gas.value))
                        ).level
                      }
                    >
                      {getGasText(
                        getGasLevel(parseInt(raspberryData.gas.value))
                      )}
                    </span>

                    {isGasAlertThreshold(parseInt(raspberryData.gas.value)) && (
                      <div
                        className={`flex items-center ${
                          isDarkMode ? "text-amber-400" : "text-amber-600"
                        }`}
                      >
                        <AlertTriangleIcon size={16} className="mr-1" />
                        <span className="text-sm">
                          Concentration trop élevée
                        </span>
                      </div>
                    )}
                  </div>
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
