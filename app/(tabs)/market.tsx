import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text, FlatList, Dimensions, StatusBar, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

export default function MarketScreen() {
  const [marketData, setMarketData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedItems, setExpandedItems] = useState({});

  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        const response = await fetch('https://backpropagators.uc.r.appspot.com/allMarketOpps');
        const data = await response.json();
        console.log(data);
        const parsedData = data.map((item, index) => ({
          id: String(index + 1),
          name: item.name,  // Adjust according to actual data structure
          opportunity: item.underlying_asset,
          potentialImpact: Array.isArray(item.impacted_markets) ? item.impacted_markets.join(', ') : item.impacted_markets,
          why: Array.isArray(item.why) ? item.why.join(', ') : item.why, // Assuming there is a "why" field in the data
          main_companies_impacted: Array.isArray(item.main_companies_impacted) ? item.main_companies_impacted.join(', ') : item.main_companies_impacted,
          potential_actions: Array.isArray(item.potential_actions) ? item.potential_actions.join(', ') : item.potential_actions

        }));
        setMarketData(parsedData);
      } catch (error) {
        console.error(error);
      }
    };
    fetchMarketData();
  }, []);

  const toggleExpand = (id) => {
    setExpandedItems(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const renderMarketItem = ({ item }) => (
    <View style={styles.marketItem} key={item.id}>
      <View style={styles.marketText}>
        <ThemedText type="subtitle" style={styles.boldText}>Opportunity:</ThemedText>
        <ThemedText style={styles.textSpacing}>{item.opportunity}</ThemedText>
        <ThemedText type="subtitle" style={styles.boldText}>Why:</ThemedText>
        <ThemedText style={styles.textSpacing}>{item.why}</ThemedText>
        {expandedItems[item.id] && (
          <>
            <ThemedText type="subtitle" style={styles.boldText}>Industries of Impact</ThemedText>
            <ThemedText style={styles.textSpacing}>{item.potentialImpact}</ThemedText>
            <ThemedText type="subtitle" style={styles.boldText}>Potential Impact:</ThemedText>
            <ThemedText style={styles.textSpacing}>{item.main_companies_impacted}</ThemedText>
            <ThemedText type="subtitle" style={styles.boldText}>Potential Actions:</ThemedText>
            <ThemedText style={styles.textSpacing}>{item.potential_actions}</ThemedText>
            
          </>
        )}
      </View>
      <TouchableOpacity onPress={() => toggleExpand(item.id)}>
        <Ionicons name="arrow-forward-outline" size={24} color="black" />
      </TouchableOpacity>
    </View>
  );

  return (
    <FlatList
      data={marketData}
      renderItem={renderMarketItem}
      keyExtractor={item => item.id}
      contentContainerStyle={styles.flatListContent}
      onEndReachedThreshold={0.5}
      ListHeaderComponent={
        <>
          <ThemedView style={styles.titleContainer}>
            <ThemedText type="title">Market Opportunities</ThemedText>
          </ThemedView>
          <ThemedText style={styles.subtitle}>Explore potential market opportunities.</ThemedText>
        </>
      }
      ListFooterComponent={
        loading ? (
          <View style={styles.loading}>
            <ThemedText>Loading...</ThemedText>
          </View>
        ) : null
      }
    />
  );
}

const styles = StyleSheet.create({
  flatListContent: {
    paddingTop: StatusBar.currentHeight + 20,
    paddingBottom: 20,
    backgroundColor: '#f0f0f0', // Consistent background color
  },
  titleContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 40, // Move down the title text
    backgroundColor: '#f0f0f0', // Background color matching the rest of the page
    paddingVertical: 10,
  },
  subtitle: {
    fontSize: 18,
    textAlign: 'center',
    marginVertical: 10,
  },
  marketItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    marginVertical: 10,
    backgroundColor: '#fff',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 2,
    width: Dimensions.get('window').width - 40,
    marginHorizontal: 20,
    position: 'relative',
  },
  marketText: {
    flex: 1,
    marginRight: 10,
  },
  boldText: {
    fontWeight: 'bold',
  },
  textSpacing: {
    marginBottom: 10,
  },
  loading: {
    paddingVertical: 20,
    alignItems: 'center',
  },
});
